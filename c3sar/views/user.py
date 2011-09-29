import formencode
from formencode import validators

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
    )

import re
import random
import string


class UniqueUsername(validators.FancyValidator):
    """
    check if username already exists in database
    """
    def _to_python(self, username, state):
        if User.get_by_username(username):
            raise formencode.Invalid(
                'That username already exists', username, state)
        return username


class RegistrationSchema(formencode.Schema):
    """
    formencode schema for user registration
    """
    allow_extra_fields = True
    username = formencode.All(validators.PlainText(not_empty = True),
                              UniqueUsername())
    password = formencode.validators.PlainText(not_empty = True)
    email = formencode.validators.Email(
        resolve_domain = False, not_empty=True)
    surname =  formencode.validators.String(not_empty = True)
    lastname =  formencode.validators.String(not_empty = True)
    #password =  formencode.validators.String(not_empty = True)
    confirm_password =  formencode.validators.String(not_empty = True)
    chained_validators = [
        formencode.validators.FieldsMatch('password', 'confirm_password')
        ]

class SecurePassword(validators.FancyValidator):
    """
    check for the password to be secure

    see
    http://formencode.org/Validator.html#writing-your-own-validator
    """
    #min = 8 #ToDo XXX
    min = 1
    non_letter = 1
    letter_regex = re.compile(r'[a-zA-Z]')

    messages = {
        'too_few': 'Your password must be longer than %(min)i '
                  'characters long',
        'non_letter': 'You must include at least %(non_letter)i '
                     'characters in your password',
        }

    def _to_python(self, value, state):
        # _to_python gets run before validate_python.  Here we
        # strip whitespace off the password, because leading and
        # trailing whitespace in a password is too elite.
        return value.strip()

    def validate_python(self, value, state):
        if len(value) < self.min:
            raise Invalid(self.message("too_few", state,
                                       min=self.min),
                          value, state)
        non_letters = self.letter_regex.sub('', value)
        if len(non_letters) < self.non_letter:
            raise Invalid(self.message("non_letter",
                                        non_letter=self.non_letter),
                          value, state)

@view_config(route_name='register',
             permission='view',
             renderer='templates/user_register.pt')
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

    URL = "diogenes:6543"
    # ToDo XXX change this to be more generic

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash(form.data['username'])
        request.session.flash(form.data['password'])
        request.session.flash(form.data['surname'])
        request.session.flash(form.data['lastname'])
        request.session.flash(form.data['email'])

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
            EmailAddress(email_address=form.data['email'])
            ]

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
# url structure: /user/confirm/{code}/{user_name}
def user_confirm_email(request):
    # values from URL/matchdict
    conf_code = request.matchdict['code']
    user_name = request.matchdict['user_name']
    user_email = request.matchdict['user_email']
    # XXX ToDo: refactor to also check email-address belongs to user...
    #get matching user from db
    user = User.get_by_username(user_name)
    print "--- in users.py:confirm_email: type(user): " + str(type(user))

    # if database says already confirmed:
    if user.email_conf == True:
        #request.session.flash('Your email address is confirmed already!')
        return { 'result_msg': "Your email is verified already!" }

    #request.session.flash("code from db: " + user.user_email_conf_code)
    #request.session.flash("is already conf'ed: " + str(user.user_email_conf))

    result = (conf_code == user.user_email_conf_code)
    if (result == True):
        #request.session.flash("result is True")
        result_msg = "your email has been successfully verified!"
        # now set confirmed to True in db
        user.user_email_conf = True
        
    else:
        #request.session.flash("result is False")
        result_msg = "Verification has failed. Bummer!"

    return {
        'result_msg': result_msg,
        }

######################################################## user_login
class LoginSchema(formencode.Schema):
    allow_extra_fields = True
    username = formencode.validators.PlainText(not_empty=True)
    password = formencode.validators.PlainText(not_empty=True)
    

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

# formencode schema for user settings ####################################
class UserSettingsSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
#    username = formencode.All(validators.PlainText(not_empty = True),
#                              UniqueUsername())
#    new_password = formencode.validators.PlainText(not_empty = True)
#    confirm_password =  formencode.validators.String(not_empty = True)
#    user_email = formencode.validators.Email(resolve_domain = False, not_empty=True)
    surname =  formencode.validators.String(not_empty = True)
    lastname =  formencode.validators.String(not_empty = True)
#    password =  formencode.validators.String(not_empty = True)
#    chained_validators = [
#        formencode.validators.FieldsMatch('new_password', 'confirm_password')
#        ]


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

    user_id = request.matchdict['user_id']
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



## formencode schema for user default license 
class UserDefaultLicenseSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True


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


# ## get contract as pdf for printout
# @view_config(route_name='user_bv_de', 
#              #permission='view',
#              permission='editUser'
#              )
# # url scheme: /user/bv/<id>
# def user_get_bv(request):
#     """
#     get a PDF for the user to print out, sign and mail back
#     """
#     dbsession = DBSession()

#     user_id = request.matchdict['user_id']
# #    user = User.get_by_user_id(user_id)

#     from pyramid.response import Response
#     response = Response(content_type='application/pdf')
# #    print "=== dir(request.url): " + str(dir(request.url))
#     # 'url', 'urlargs', 'urlvars'
# #    print "=== request.: " + str(request.)
# #    print "=== request.url: " + str(request.url)
# #    print "=== request.resource_url(): " + str(request.resource_url())
# #    print "=== request.urlargs: " + str(request.urlargs)
# #    print "=== request.urlvars: " + str(request.urlvars)
# #    print "=== dir(response): " + str(dir(response))
# #    print "=== response.location: " + str(response.location)
#     response.app_iter = open('pdftk/output.pdf')
#     return response


# # from pyramid.httpexceptions import HTTPMovedPermanently
# # response = HTTPMovedPermanently(location=new_url)
# #
# #
# #

@view_config(route_name='user_contract_de', 
             permission='view',
             #permission='editUser'
             )
# url scheme: /user/bv/C3S_contract_de.<SurnameLastname>
def user_contract_de(request):
    """
    get a PDF for the user to print out, sign and mail back
    """
    dbsession = DBSession()
    from fdfgen import forge_fdf
    user_id = request.matchdict['user_id']

    # check if user is not logged in
    if user_id == 'blank':
        print "===== user is not logged in"
        
        #generate fdf string
        fdf = forge_fdf("", [], [], [], [])
        # write to file
        my_fdf_filename = "fdf_blank.fdf"
        import os
        fdf_file = open(my_fdf_filename , "w")
        fdf_file.write(fdf)
        fdf_file.close()
        print "fdf file written."
        #print os.popen('pwd').read()
        print os.popen('pdftk pdftk/berechtigungsvertrag-2.2_outlined.pdf fill_form %s output formoutput.pdf flatten'% my_fdf_filename).read()
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
#open('pdftk/output.pdf')
    return response


# from pyramid.httpexceptions import HTTPMovedPermanently
# response = HTTPMovedPermanently(location=new_url)
#
#
#


@view_config(route_name='user_contract_de_username', 
             permission='view',
             #permission='editUser'
             )
# url scheme: /user/bv/C3S_contract_de.<Username>
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
        
        #generate fdf string
        fdf = forge_fdf("", [], [], [], [])
        # write to file
        my_fdf_filename = "fdf_blank.fdf"
        import os
        fdf_file = open(my_fdf_filename , "w")
        fdf_file.write(fdf)
        fdf_file.close()
        print "fdf file written."
        #print os.popen('pwd').read()
        print os.popen('pdftk pdftk/berechtigungsvertrag-2.2_outlined.pdf fill_form %s output formoutput.pdf flatten'% my_fdf_filename).read()
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
#open('pdftk/output.pdf')
    return response


# from pyramid.httpexceptions import HTTPMovedPermanently
# response = HTTPMovedPermanently(location=new_url)
#
#
#
