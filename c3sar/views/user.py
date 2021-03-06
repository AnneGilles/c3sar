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
    Group,
    )

import os
import random
import string
from types import NoneType
from datetime import datetime

from c3sar.views.validators import (
    UniqueUsername,
    RegistrationSchema,
    SecurePassword,
    LoginSchema,
    UserSettingsSchema,
    UserDefaultLicenseSchema,
    )


dbsession = DBSession()
DEBUG = False


#@view_config(route_name='register',
#             permission='view',
#             renderer='templates/user_add.pt')
def user_register(request):
    """
    a user registers with the system
    """
    DEBUG = False
    form = Form(request, RegistrationSchema)
    #mailer = get_mailer(request)

    # create a random string for email verification procedure
    # http://stackoverflow.com/questions/2257441/
    #   python-random-string-generation-with-upper-case-letters-and-digits
    N = 6
    randomstring = ''.join(random.choice(string.ascii_uppercase
                                         + string.digits) for x in range(N))
    #print " -- the random string: " + randomstring

    URL = "localhost:6543"
    # ToDo XXX change this to be more generic

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        if DEBUG:  # pragma: no cover
            print "submitted, but not validated"
    else:  # pragma: NO COVER # just for debugging, RLY
        if DEBUG:
            print "form.submitted was not seen"
        pass

    if 'form.submitted' in request.POST and form.validate():
        # ready for registration!
        #request.session.flash('form validated!')
        username = unicode(form.data['username'])

        message = Message(
            subject="C3S: confirm your email address",
            sender="noreply@c-3-s.org",
            recipients=[form.data['email']],
            body="Hello, " + form.data['surname'] + ", \n"
            "Please confirm your email address by clicking this link: \n"
            "http://" + URL + "/user/confirm/" + randomstring + "/"
            + form.data['username'] + " \n"
            "Thanks!")
        msg_accountants = Message(
            subject="[C3S] new member registration",
            sender="noreply@c-3-s.org",
            recipients=['christoph@infinipool.com'],
            body="Hello \n"
            "A new member has registered with your site: \n"
            "Username: " + form.data['username'] + " \n"
            "First name: " + form.data['surname'] + " \n"
            "Last name: " + form.data['lastname'] + " \n"
            "Email: " + form.data['email'] + " \n"
            "Thanks!")

        user = User(
            username=username,
            password=unicode(form.data['password']),
            surname=unicode(form.data['surname']),
            lastname=unicode(form.data['lastname']),
            email=unicode(form.data['email']),
            email_is_confirmed=False,
            email_confirm_code=unicode(randomstring),
            phone=unicode(form.data['phone']),
            fax=unicode(form.data['fax']),
            )
        user.set_address(street=unicode(form.data['street']),
                         number=unicode(form.data['number']),
                         postcode=unicode(form.data['postcode']),
                         city=unicode(form.data['city']),
                         country=unicode(form.data['country']),
                         )

        user_group = Group.get_Users_group()
        user.groups = [user_group]

        # dbsession.add(user)
        dbsession.flush(user)

        #
        # boto stuff: creating a bucket for that user
        # don't do that -- we better have one bucket for all tracks...
        #
        # from boto.exception import S3CreateError, BotoServerError
        # try:
        #     c3sI2Conn.create_named_bucket(username)
        #     request.session.flash(u'created bucket for ' + username)
        # except BotoServerError, e:
        #     print("There was an error: " + str(e) )
        # except S3CreateError, e:
        #     print("There was an error: " + str(e) )
        #
        # send email
        try:
            if DEBUG:  # pragma: no cover
                print("sending email........")
            else:
                pass
            #mailer.send(message)
            #mailer.send(msg_accountants)

            # instead of sending mails, we inform in-browser
            request.session.flash(
                'DEBUG: not sending email. to test email confirmation view, '
                'append this to URL to confirm email: /user/confirm/'
                + randomstring + '/'
                + str(user.username) + '/' + str(form.data['email']))
        except:  # pragma: no cover
            print "could not send email. no mail configured?"

        # remember who this was == sign in user == log her in
        headers = remember(request, username)

        redirect_url = route_url('home', request)

        return HTTPFound(location=redirect_url, headers=headers)

    return {'form': FormRenderer(form), }


@view_config(route_name='confirm_email',
             permission='view',
             renderer='../templates/user_confirm_email.pt')
# url structure: /user/confirm/{code}/{user_name}/{user_email}
def user_confirm_email(request):
    """
    this view takes three arguments from the URL aka request.matchdict
    - code
    - user name
    - user email
    and tries to match them to database entries.
    if matching is possible,
    - the email address in question is confirmed as validated
    - the database entry is changed to reflect this
    """
    # values from URL/matchdict
    conf_code = request.matchdict['code']
    user_name = request.matchdict['user_name']
    user_email = request.matchdict['user_email']

    #get matching user from db
    user = User.get_by_username(user_name)

    # check if the information in the matchdict makes sense
    #  - user
    if isinstance(user, NoneType):
        #print "user is of type NoneType"
        return {
            'result_msg':
            "Something didn't work. "
            "Please check whether you tried the right URL."
            }
    # - email
    if (user.email == user_email):
        #print "this one matched! " + str(user_email)

        if (user.email_is_confirmed):
            #print "confirmed already"
            return {'result_msg': "Your email address was confirmed already."}
        # - confirm code
        #print "checking confirmation code..."
        if (user.email_confirm_code == conf_code):
            #print "conf code " + str(conf_code)
            #print "user.conf code " + str(user.email_confirm_code)

            #print " -- found the right confirmation code in db"
            #print " -- set this email address as confirmed."
            user.email_is_confirmed = True
            return {'result_msg':
                    "Thanks! Your email address has been confirmed."}
    # else
    return {'result_msg': "Verification has failed. Bummer!"}


######################################################## user_login
#@view_config(route_name='login',
#             permission='view',
#             renderer='../templates/login.pt')
def login_view(request):
    DEBUG = False
    msg = u''
    if DEBUG:  # pragma: no cover
        print "this is login_view"

    # see https://github.com/Pylons/pyramid/blob/master/docs/tutorials/
    #                         wiki2/src/authorization/tutorial/views.py
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:  # pragma: no cover
        referrer = '/'
    came_from = request.params.get('came_from', referrer)

    headers = None
    logged_in = authenticated_userid(request)
    if logged_in is not None:  # need to find testcase to cover...
        request.session.flash('you are logged in already!')
        #print('you are logged in already!')
        return HTTPFound(location=came_from,
                         headers=headers)

    if logged_in is None:
        request.session.pop_flash()

    form = Form(request, LoginSchema)

    logged_in = authenticated_userid(request)
    request.session.flash(logged_in)

    login = ''
    password = ''

    post_data = request.POST

    if not 'submit' in post_data:
        if DEBUG:  # pragma: no cover
            request.session.flash('not submitted!')
            print "not submitted"

    if 'submit' in post_data and not form.validate():
        if DEBUG:  # pragma: no cover
            request.session.flash(u'form didnt validate')
            print 'form didnt validate'

    if 'submit' in post_data and form.validate():

        login = post_data['username']
        if DEBUG:  # pragma: no cover
            request.session.flash(u'username: ' + login)
            print u'username: ' + str(login)

        password = post_data['password']
        if DEBUG:  # pragma: no cover
            request.session.flash(password)
            print "password: " + str(password)
        if User.check_password(login, password):
            if DEBUG:  # pragma: no cover
                request.session.flash(u'User.check_password was True!')
                request.session.flash(u'login: ' + login)
                print 'User.check_password was True!'
            headers = remember(request, login)

            #home_view = route_url('home', request)
            #came_from = request.params.get('came_from', home_view)

            if DEBUG:  # pragma: no cover
                request.session.flash(u'Logged in successfully.')
                print 'Logged in successfully.'
                #print "home_view: " + str(home_view)
                #print "came_from: " + str(came_from)
                print "will login the user and redirect her"
            return HTTPFound(
                location=route_url(u'home', request=request), headers=headers)

        else:
            request.session.flash(
                u"username and password didn't match!",  # message
                'passwordcheck')                        # to queue
            msg = u"username and password didn't match!"
            if DEBUG:  # pragma: no cover
                request.session.flash(u'User.check_password was NOT True!')
                print 'User.check_password was NOT True!'
                request.session.flash(
                    u'account not found or passwords didnt match')

    if DEBUG:  # pragma: no cover
        request.session.flash(u'Failed to login. Musta been errors!')
        print "returning the form"
    return {
        'form': FormRenderer(form),
        'msg': msg,
        }


############################################################ user_logout
@view_config(permission='view',
             route_name='logout'
             )
def logout_view(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location=route_url('home', request),
                     headers=headers)


############################################################ user_list
@view_config(route_name='user_list',
             permission='view',
             renderer='../templates/user_list.pt')
def user_list(request):
    users = User.user_listing(User.id.desc())
    return {'users': users}


#@view_config(route_name='user_view',
#             permission='view',
#             renderer='../templates/user_view.pt')
def user_view(request):
    user_id = request.matchdict['user_id']
    user = User.get_by_user_id(user_id)

    if isinstance(user, NoneType):
        return HTTPFound(location=route_url('not_found', request))

    # calculate for next/previous navigation
    max_id = User.get_max_id()
    # previous
    if user.id == 1:            # if looking at first id
        prev_id = max_id        # --> choose highest db row, 'wrap around'
    else:                       # if looking at any other id
        prev_id = user.id - 1   # --> choose previous
    # next
    if user.id != max_id:       # if not on highest id
        next_id = user.id + 1   # --> choose next
    elif user.id == max_id:     # if highest id
        next_id = 1             # --> choose first id ('wrap around'))

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

from pyramid.security import has_permission
from pyramid.httpexceptions import HTTPForbidden


# ################################################################### user_edit
# #from formencode import htmlfill
# from c3sregistration.security import UserContainer
#@view_config(route_name='user_edit',
#             #permission='view',
#             permission='editUser',
#             context=UserContainer,
#             renderer='../templates/user_edit_table.pt')
def user_edit(request):
    """
    let users change some of their details
    """
    DEBUG = False

    if not has_permission('editUser', request.context, request):
        #print "NOT has_permission !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        request.message = "You do not have permissions to edit this user!"
        raise HTTPForbidden

   # if no user_id in URL and not logged in, tell user to login

    try:
        user_id = request.matchdict['user_id']
    except KeyError, ke:
        #print ke
        return HTTPFound(location=request.route_url('not_found'))

    user = User.get_by_user_id(user_id)

    if user is None:
        msg = "User was not founf in database."
        return HTTPFound(location=request.route_url('not_found'))

    form = Form(request, schema=UserSettingsSchema, obj=user)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('Please check the form below for errors!')
        if DEBUG:  # pragma: no cover
            print "submitted but not validated!"

    if 'form.submitted' in request.POST and form.validate():
        # ready for changing database entries!
        request.session.flash('form validated!')
        if DEBUG:  # pragma: no cover
            print "the form was submitted and validated."

        if form.data['surname'] != user.surname:
            if DEBUG:  # pragma: no cover
                request.session.flash('surname was not same --> changing')
                print "changing surname"
            user.surname = form.data['surname']
        if form.data['lastname'] != user.lastname:
            if DEBUG:  # pragma: no cover
                request.session.flash('lastname was not same --> changing')
                print "changing lastname"
            user.lastname = form.data['lastname']
        if form.data['email'] != user.email:
            request.session.flash('email was not same --> changing')
            user.email = form.data['email']
        if form.data['phone'] != user.phone:
            request.session.flash('phone was not same --> changing')
            user.phone = form.data['phone']
        if form.data['fax'] != user.fax:
            request.session.flash('fax was not same --> changing')
            user.fax = form.data['fax']
        if form.data['street'] != user.street:
            request.session.flash('street was not same --> changing')
            user.street = form.data['street']
        if form.data['number'] != user.number:
            request.session.flash('number was not same --> changing')
            user.number = form.data['number']
        if form.data['city'] != user.city:
            request.session.flash('city was not same --> changing')
            user.city = form.data['city']
        if form.data['postcode'] != user.postcode:
            request.session.flash('postcode was not same --> changing')
            user.postcode = form.data['postcode']
        if form.data['country'] != user.country:
            request.session.flash('country was not same --> changing')
            user.country = form.data['country']

    if DEBUG:  # pragma: no cover
        print "returning the form"
    return {
        'the_user_id': user_id,
        'the_username': user.username,
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

    form = Form(request, schema=UserDefaultLicenseSchema, obj=user)

    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')

    return {
        'the_user_id': user_id,
        'the_username': user.username,
        'form': FormRenderer(form),
        }


def generate_contract_de_fdf_pdf(user):
    """
    take user information and generate fdf
    """
    if DEBUG:  # pragma: no cover
        print "===== this is generate_fdf_pdf"
    from fdfgen import forge_fdf
    fields = [
        ('surname', user.surname),
        ('lastname', user.lastname),
        ('street', user.street),
        ('number', user.number),
        ('postcode', user.postcode),
        ('city', user.city),
        ('email', user.email),
        ('user_id', user.id),
        ('username', user.username),
        ('date_registered', user.date_registered),
        ('date_generated', datetime.now()),
        ]
    #generate fdf string
    fdf = forge_fdf("", fields, [], [], [])
    # write to file
    my_fdf_filename = "fdf" + str(user.id) + ".fdf"

    fdf_file = open(my_fdf_filename, "w")
    fdf_file.write(fdf)
    fdf_file.close()
    if DEBUG:  # pragma: no cover
        print "fdf file written."

    res = os.popen(
        'pdftk pdftk/berechtigungsvertrag-2.2.pdf fill_form %s output'
        ' formoutput.pdf flatten' % my_fdf_filename).read()

    if DEBUG:  # pragma: no cover
        print res
        print "done: put data into form and finalized it"

    # delete the fdf file
    res = os.popen('rm %s' % my_fdf_filename)
    if DEBUG:  # pragma: no cover
        print res
        print "combining with bank account form"
    # combine
    res = os.popen(
        'pdftk formoutput.pdf pdftk/bankaccount.pdf output output.pdf').read()
    if DEBUG:  # pragma: no cover
        print res
        print "combined personal form and bank form"

    # delete the fdf file
    os.popen('rm formoutput.pdf').read()

    # return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    response.app_iter = open("output.pdf", "r")
    return response


@view_config(route_name='user_contract_de_username',
             permission='view',
             #permission='editUser'
             )
# url scheme: /user/bv/C3S_contract_.<Username>.pdf
def user_contract_de_username(request):
    """
    get a PDF for the user to print out, sign and mail back

    special feature: username in filename
    """

    try:
        username = request.matchdict['username']
        user = User.get_by_username(username)
        assert(isinstance(user, User))
        if DEBUG:  # pragma: no cover
            print "about to generate pdf for user " + str(user.username)
        return generate_contract_de_fdf_pdf(user)
    except Exception, e:
        if DEBUG:  # pragma: no cover
            print "something failed:"
            print e
        return HTTPFound(location=route_url('home', request))


#@view_config(route_name='user_login_first',
#             permission='view',
#             renderer='../templates/have_to_login.pt')
# this ^ view config ^ is unnecessary/invalid, config done in __init__.py
def user_login_first(request):
    return dict(msg='log in first')
