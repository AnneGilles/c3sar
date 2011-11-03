from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )
from pyramid.url import route_url
from pyramid.view import view_config

from c3sar.models import (
    DBSession,
    User,
    EmailAddress,
    PhoneNumber,
    )

import os
import random
import string

from c3sar.views.validators import (
    UniqueUsername,
    RegistrationSchema,
    SecurePassword,
    LoginSchema,
    UserSettingsSchema,
    UserDefaultLicenseSchema,
    )


#@view_config(route_name='register',
#             permission='view',
#             renderer='templates/user_add.pt')
def user_register(request):
    """
    a user registers with the system
    """

    form = Form(request, RegistrationSchema)
    #mailer = get_mailer(request)

    # create a random string for email verification procedure
    # http://stackoverflow.com/questions/2257441/
    #   python-random-string-generation-with-upper-case-letters-and-digits
    N=6
    randomstring = ''.join(random.choice(string.ascii_uppercase
                                         + string.digits) for x in range(N))
    #print " -- the random string: " + randomstring

    URL = "diogenes:6543"
    # ToDo XXX change this to be more generic

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        #request.session.flash(form.data['username'])
        #request.session.flash(form.data['password'])
        #request.session.flash(form.data['surname'])
        #request.session.flash(form.data['lastname'])
        #request.session.flash(form.data['email'])

    if 'form.submitted' in request.POST and form.validate():
        # ready for registration!
        request.session.flash('form validated!')
        dbsession = DBSession()
        username = form.data['username']


        message = Message(subject = "C3S: confirm your email address",
                          sender = "noreply@c-3-s.org",
                          recipients = [form.data['email']],
                          body = "Hello, " + form.data['surname'] + ", \n"
                          "Please confirm your email address by clicking this link: \n"
                          "http://" + URL + "/user/confirm/" +  randomstring + "/"
                          + form.data['username'] + " \n"
                          "Thanks!")
        msg_accountants = Message(subject = "[C3S] new member registration",
                          sender = "noreply@c-3-s.org",
                          recipients = ['christoph@infinipool.com'],
                          body = "Hello \n"
                          "A new member has registered with your site: \n"
                          "Username: " + form.data['username'] +  " \n"
                          "First name: " + form.data['surname'] +  " \n"
                          "Last name: " + form.data['lastname'] +  " \n"
                          "Email: " + form.data['email'] +  " \n"
                          "Thanks!")

        user = User(
            username = username,
            password = form.data['password'],
            surname = form.data['surname'],
            lastname = form.data['lastname'],
            )

        user.email_addresses = [
            EmailAddress(
                email_address = form.data['email'],
                conf_code = randomstring,
                )
            ]

        user.phone_numbers.append(
            PhoneNumber(phone_number=form.data['phone'])
            )

        user.set_address(street=form.data['street'],
                         number=form.data['number'],
                         postcode=form.data['postcode'],
                         city=form.data['city'],
                         country=form.data['country'],
                         )

#        user.groups.append('User')
        dbsession.add(user)

        # boto stuff: creating a bucket for that user
        # don't do that -- we better have one bucket for all tracks...

        # from boto.exception import S3CreateError, BotoServerError
        # try:
        #     c3sI2Conn.create_named_bucket(username)
        #     request.session.flash(u'created bucket for ' + username)
        # except BotoServerError, e:
        #     print("There was an error: " + str(e) )
        # except S3CreateError, e:
        #     print("There was an error: " + str(e) )


        # send email
        try:
            print("sending email........")
            #mailer.send(message)
            #mailer.send(msg_accountants)

            # instead of sending mails, we inform in-browser
            request.session.flash('DEBUG: not sending email. to test email confirmation view, click here: <a href="/user/confirm/' + randomstring + '/' + str(user.username) + '/' + str(form.data['email']) + '">Confirm Email</a>')
        except:
            print "could not send email. no mail configured?"

        # remember who this was == sign in user == log her in
        headers = remember(request, username)

        redirect_url = route_url('home', request)


        return HTTPFound(location = redirect_url, headers=headers)

    return {
        'form': FormRenderer(form),
        }


@view_config(route_name='confirm_email',
             permission='view',
             renderer='../templates/user_confirm_email.pt')
# url structure: /user/confirm/{code}/{user_name}/{user_email}
def user_confirm_email(request):
    """
    this view takes two arguments from the URL aka request.matchdict
    - code
    - user_name
    and tries to match them to database entries.
    if matching is possible,
    - the email address in question is confirmed as validated
    - the database entry is changed to reflect this
    """
    DEBUG = True
    # values from URL/matchdict
    conf_code = request.matchdict['code']
    user_name = request.matchdict['user_name']
    user_email = request.matchdict['user_email']
    # XXX ToDo: refactor to also check email-address belongs to user...
    if DEBUG:
        print " -- confirmation code: " + conf_code
        print " -- user name: " + user_name
        print " -- user email: " + user_email

    dbsession = DBSession()
    #get matching user from db
    user = User.get_by_username(user_name)
    if DEBUG: print "--- in users.py:user_confirm_email: type(user): " + str(type(user))

    # check if the information in the matchdict makes sense
    #  - user
    #  -
    from types import NoneType
    if isinstance(user, NoneType):
        print "user is of type NoneType"
        return {'result_msg': "Something didn't work. Please check whether you tried the right URL."}

    # get all email addresses of that user into a list
    for item in user.email_addresses:

        if (item.email_address == user_email):
            print "this one matched!"

            if (item.is_confirmed):
                return {'result_msg': "Your email address was confirmed already." }

            if (item.confirm_code == conf_code):
                print " -- found the right confirmation code in db"
                item.is_confirmed = True
                print " -- set this email address as confirmed."
                return {'result_msg': "Thanks! You email address has been confirmed." }
    # else
    return {'result_msg': "Verification has failed. Bummer!"}

######################################################## user_login

#@view_config(route_name='login',
#             permission='view',
#             renderer='../templates/login.pt')
def login_view(request):

    came_from = "space"
    headers = None
    logged_in = authenticated_userid(request)
    if logged_in is not None:
        request.session.flash('you are logged in already!')
        return HTTPFound(location = came_from, headers=headers)

    # test for csrf token
    #request.session.flash('token?: ' + str(request.POST.get("_csrf")))
    # results in message: ['token?: d593dc44ff2012385df0abc5e371b4a5503b0c46'

    if logged_in is None:
        request.session.pop_flash()

    form = Form(request, LoginSchema)

    home_view = route_url('home', request)
    came_from = request.params.get('came_from', home_view)

#    login_url = resource_url(request.context, request, 'login')
#    login_url = request.url
#    referrer = request.url
    logged_in = authenticated_userid(request)
    loggedin =  authenticated_userid(request)
    request.session.flash(logged_in)

#    if referrer == login_url:
#        referrer = '/'

#    came_from = request.params.get('came_from', referrer)

    username = ''
    message = ''
    login = ''
    password = ''

    post_data = request.POST
    #request.session.flash(post_data)

    if not 'submit' in post_data:
        request.session.flash('not submitted!')

    if 'submit' in post_data and not form.validate():
        request.session.flash(u'-- form didnt validate')

    if 'submit' in post_data and form.validate():

        login = post_data['username']
        request.session.flash(u'username: ' + login)

        password = post_data['password']
        request.session.flash(password)

        if User.check_password(login, password):
            request.session.flash(u'User.check_password was True!')
            request.session.flash(u'login: ' + login)
            headers = remember(request, login)
            request.session.flash(u'Logged in successfully.')
            return HTTPFound(location = came_from, headers=headers)

        else:
            request.session.flash(u'User.check_password was NOT True!')
            request.session.flash(u'account not found or passwords didnt match')

    request.session.flash(u'Failed to login. Musta been errors!')
    return {
        'form': FormRenderer(form),
        }

############################################################ user_logout
@view_config(permission='view',
             route_name='logout'
             )
def logout_view(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location = route_url('home', request),
                     headers = headers)

############################################################ user_list
@view_config(route_name='user_list',
             permission='view',
             renderer='../templates/user_list.pt')
def user_list(request):
    users = User.user_listing(User.id.desc())
    return {'users': users}


#################################################################### user_view
@view_config(route_name='user_view',
             permission='view',
             renderer='../templates/user_view.pt')
def user_view(request):
    user_id = request.matchdict['user_id']
    user = User.get_by_user_id(user_id)

    # calculate for next/previous navigation
    prev_id = int(user_id) - 1
    next_id = int(user_id) + 1
    # ToDo: what if foo_id == 0 or nonexistant?
    # maybe use template logic to not show prev-next-link?
    # maybe try to figure out max_id? what is cheaper? just fail/404?
    # we need the 404 anyway, if user picks random url/user_id

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)

    return {
        'blank': 'blank',
        'user': user,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id,
        }

#################################################################### user_view
@view_config(route_name='user_profile',
             permission='view',
             renderer='../templates/user_profile.pt')
def user_profile(request):
    user_id = request.matchdict['user_id']
    user = User.get_by_user_id(user_id)

    # calculate for next/previous navigation
    prev_id = int(user_id) - 1
    next_id = int(user_id) + 1
    # ToDo: what if foo_id == 0 or nonexistant?
    # maybe use template logic to not show prev-next-link?
    # maybe try to figure out max_id? what is cheaper? just fail/404?
    # we need the 404 anyway, if user picks random url/user_id

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)

    return {
        'user': user,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id,
        }



# #################################################################### user_edit
# #from formencode import htmlfill
# from c3sregistration.security import UserContainer


@view_config(route_name='user_edit',
             #permission='view',
             permission='editUser',
#             context=UserContainer,
             renderer='../templates/user_edit_table.pt')
def user_edit(request):
    """
    let users change some of their details
    """
    dbsession = DBSession()

    # if no user_id in URL and not logged in, tell user to login

    try:
        user_id = request.matchdict['user_id']
    except:
        print "no user_id in matchdict !!!"
        return HTTPFound(location=request.route_url('user_login_first'))

    user = User.get_by_user_id(user_id)

#    request.session.flash("email confirmed? " + str(user.user_email_conf))
#    if user.email_conf == True:
#        email_is_confirmed = "Yes"
#    else:
#        email_is_confirmed = "No"

    form = Form(request, schema = UserSettingsSchema, obj = user)


    if form.validate():
        request.session.flash("Yes! form.validate() !!!")


    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash(form.data['user_surname'])
        request.session.flash(form.data['user_lastname'])
        request.session.flash(form.data['user_email'])

    if 'form.submitted' in request.POST and form.validate():
        # ready for registration!
        request.session.flash('form validated!')
        #username = form.data['username']

        # user = User(
        #     username = user.username,
        #     #password = form.data['password'],
        #     user_surname = form.data['user_surname'],
        #     user_lastname = form.data['user_lastname'],
        #     user_email = form.data['user_email']
        #     )

        if form.data['surname'] !=  user.surname:
            request.session.flash('surname was not same --> changing')
            user.surname = form.data['surname']

        if form.data['lastname'] !=  user.lastname:
            request.session.flash('lastname was not same --> changing')
            user.lastname = form.data['lastname']

#        if form.data['user_email'] !=  user.email:
#            request.session.flash('email was not same --> changing')
#            user.user_email = form.data['user_email']

# ToDo
        # if form.data['user_telephone'] !=  user.user_telephone:
        #     request.session.flash('telephone was not same --> changing')
        #     user.user_telephone = form.data['user_telephone']

        # if form.data['user_telefax'] !=  user.user_telefax:
        #     request.session.flash('telefax was not same --> changing')
        #     user.user_telefax = form.data['user_telefax']



        #redirect_url = route_url('user_view', request)


#       return HTTPFound(location = redirect_url, headers=headers)
       # return dict (
       #     message = 'You won!'
       #     )


    return {
        'the_user_id': user_id,
        'the_username': user.username,
 #       'email_is_confirmed': email_is_confirmed,
        'form': FormRenderer(form),
        }




## default license
@view_config(route_name='user_set_default_license',
             #permission='view',
             permission='editUser',
#             context=UserContainer,
             renderer='../templates/user_set_default_license.pt')
def user_set_default_license(request):
    """
    let users change some of their details
    """
    dbsession = DBSession()

    user_id = request.matchdict['user_id']
    user = User.get_by_user_id(user_id)

    form = Form(request, schema = UserDefaultLicenseSchema, obj = user)


    if 'form.submitted' in request.POST and form.validate():
        # ready for registration!
        request.session.flash('form validated!')

# ToDo XXX
        # user = User(
        #     username = user.username,
        #     #password = form.data['password'],
        #     user_surname = form.data['user_surname'],
        #     user_lastname = form.data['user_lastname'],
        #     user_email = form.data['user_email']
        #     )

        # if form.data['surname'] !=  user.surname:
        #     request.session.flash('surname was not same --> changing')
        #     user.surname = form.data['surname']

        # if form.data['lastname'] !=  user.lastname:
        #     request.session.flash('lastname was not same --> changing')
        #     user.lastname = form.data['lastname']

#        if form.data['user_email'] !=  user.email:
#            request.session.flash('email was not same --> changing')
#            user.user_email = form.data['user_email']

# ToDo
        # if form.data['user_telephone'] !=  user.user_telephone:
        #     request.session.flash('telephone was not same --> changing')
        #     user.user_telephone = form.data['user_telephone']

        # if form.data['user_telefax'] !=  user.user_telefax:
        #     request.session.flash('telefax was not same --> changing')
        #     user.user_telefax = form.data['user_telefax']



        #redirect_url = route_url('user_view', request)


#       return HTTPFound(location = redirect_url, headers=headers)
       # return dict (
       #     message = 'You won!'
       #     )


    return {
        'the_user_id': user_id,
        'the_username': user.username,
 #       'email_is_confirmed': email_is_confirmed,
        'form': FormRenderer(form),
        }


def generate_contract_de_blank():
    print "===== user is not logged in, so we will give her a contract without any data"

    # return a pdf file with a blank contract
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    response.app_iter = open("pdftk/berechtigungsvertrag-2.2_outlined.pdf" , "r")


def generate_contract_de(userid):
    # stub
    pass


@view_config(route_name='user_contract_de',
             permission='view',
             #permission='editUser'
             )
# url scheme: /user/bv/C3S_contract_de_{username}
def user_contract_de(request):
    """
    get a PDF for the user to print out, sign and mail back
    """
    dbsession = DBSession()
    from fdfgen import forge_fdf
    user_id = request.matchdict['user_id']

    print "user_id = " + str(user_id)
    # check if user is not logged in, then return blank contract
    if user_id == 'blank' or not hasattr(request.user, 'id'):
        print "user_id equalled blank"
        return generate_contract_de_blank()


    user = User.get_by_user_id(user_id)
    from datetime import datetime

    fields = [
        ('surname', request.user.surname),
        ('lastname', request.user.lastname),
        ('street', request.user.street),
        ('number', request.user.number),
        ('postcode', request.user.postcode),
        ('city', request.user.city),
        ('email', request.user.email_addresses[0].email_address),
        ('user_id', request.user.id),
        ('username', request.user.username),
        ('date_registered', request.user.date_registered),
        ('date_generated', datetime.now()),
        ]
    #generate fdf string
    fdf = forge_fdf("", fields, [], [], [])
    # write to file
    my_fdf_filename = "fdf" + str(request.user.id) + ".fdf"
    import os
    fdf_file = open(my_fdf_filename , "w")
    fdf_file.write(fdf)
    fdf_file.close()
    print "fdf file written."
    print os.popen('pwd').read()
    print os.popen('pdftk pdftk/berechtigungsvertrag-2.2.pdf fill_form %s output formoutput.%s.pdf flatten'% (my_fdf_filename, str(request.user.id)) ).read()
    print "done: put data into form and finalized it"

    # delete the fdf file
    print os.popen('rm %s'% my_fdf_filename).read()

    # combine
    print "combining with bank account form"
    print os.popen('pdftk formoutput.%s.pdf pdftk/bankaccount.pdf output output.%s.pdf' % (str(request.user.id),str(request.user.id))).read()
    print "combined personal form and bank form"

    # delete the fdf file
    print os.popen('rm formoutput.%s.pdf' % str(request.user.id)).read()

    # return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    response.app_iter = open("output.%s.pdf" % str(request.user.id) , "r")
    return response



@view_config(route_name='user_contract_de_username',
             permission='view',
             #permission='editUser'
             )
# url scheme: /user/bv/C3S_contract_.<Username>.pdf
def user_contract_de_username(request):
    """
    get a PDF for the user to print out, sign and mail back
    """
    dbsession = DBSession()
    from fdfgen import forge_fdf
    user_id = request.matchdict['username']

    # check if user is not logged in
    if user_id == 'blank':
        print "===== user is not logged in"

        # return a pdf file
        from pyramid.response import Response
        response = Response(content_type='application/pdf')
        response.app_iter = open("pdftk/berechtigungsvertrag-2.2_outlined.pdf" , "r")
        return response

    user = User.get_by_user_id(user_id)


    fields = [
        ('surname', request.user.surname),
        ('lastname', request.user.lastname),
        ('street', request.user.street),
        ('number', request.user.number),
        ('postcode', request.user.postcode),
        ('city', request.user.city),
        ('email', request.user.email_addresses[0].email_address),
        ('user_id', request.user.id),
        ('username', request.user.username),
        ('date_registered', request.user.date_registered),
        ('date_generated', datetime.now()),
        ]
    #generate fdf string
    fdf = forge_fdf("", fields, [], [], [])
    # write to file
    my_fdf_filename = "fdf" + str(request.user.id) + ".fdf"
    import os
    fdf_file = open(my_fdf_filename , "w")
    fdf_file.write(fdf)
    fdf_file.close()
    print "fdf file written."
    print os.popen('pwd').read()
    print os.popen('pdftk pdftk/berechtigungsvertrag-2.2.pdf fill_form %s output formoutput.pdf flatten'% my_fdf_filename).read()
    print "done: put data into form and finalized it"

    # delete the fdf file
    print os.popen('rm %s'% my_fdf_filename)

    # combine
    print "combining with bank account form"
    print os.popen('pdftk formoutput.pdf pdftk/bankaccount.pdf output output.pdf').read()
    print "combined personal form and bank form"

    # delete the fdf file
    print os.popen('rm formoutput.pdf').read()

    # return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    response.app_iter = open("output.pdf" , "r")
    return response


from pyramid.response import Response
@view_config(route_name='user_login_first',
             permission='view',
             renderer='../templates/have_to_login.pt')
def user_login_first(request):
    the_message = "Please login first."
    return Response(the_message)

