import formencode
from formencode import validators

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pyramid.view import view_config



from c3sar.models import User


## UniqueUsername
# check if username already exists in database

class UniqueUsername(validators.FancyValidator):
    def _to_python(self, username, state):
        if User.get_by_username(username):
            raise formencode.Invalid(
                'That username already exists', username, state)
        return username


# formencode schema for user registration 
class RegistrationSchema(formencode.Schema):
    allow_extra_fields = True
    username = formencode.All(validators.PlainText(not_empty = True),
                              UniqueUsername())
    password = formencode.validators.PlainText(not_empty = True)
    email_address = formencode.validators.Email(resolve_domain = False, not_empty=True)
    surname =  formencode.validators.String(not_empty = True)
    lastname =  formencode.validators.String(not_empty = True)
#    password =  formencode.validators.String(not_empty = True)
    confirm_password =  formencode.validators.String(not_empty = True)
    chained_validators = [
        formencode.validators.FieldsMatch('password', 'confirm_password')
        ]


## SecurePassword
# as of http://formencode.org/Validator.html#writing-your-own-validator

import re
class SecurePassword(validators.FancyValidator):
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
    """ a user registers with the system
    """

    form = Form(request, RegistrationSchema)
    #mailer = get_mailer(request)

    # create a random string for email verification procedure
    # http://stackoverflow.com/questions/2257441/
    #   python-random-string-generation-with-upper-case-letters-and-digits
    import random
    import string
    N=6
    randomstring = ''.join(random.choice(string.ascii_uppercase 
                                         + string.digits) for x in range(N))

    URL = "diogenes:6543"                       

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
        #session = DBSession()
        session = getSession()
        username = form.data['username']
                           

        message = Message(subject = "C3S: confirm your email address",
                          sender = "noreply@c-3-s.org",
                          recipients = [form.data['email']],
                          body = "Hello, " + form.data['user_surname'] + ", \n" 
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
            email = form.data['email'],
            email_conf_code = randomstring,
            email_conf = False
            )
#        user.groups.append('User')
        session.add(user)

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

        # remember who this was == sign in user
        headers = remember(request, username)
        
        redirect_url = route_url('home', request)


        return HTTPFound(location = redirect_url, headers=headers)

    return {
        'form': FormRenderer(form),
        }
