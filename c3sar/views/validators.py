import re
import formencode
from formencode import validators
from c3sar.models import (
    User,
    )


class UniqueUsername(validators.FancyValidator):
    """
    check if username already exists in database
    and make sure it is unique / does not exist in db

    if not unique, raise error
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
    username = formencode.All(validators.PlainText(not_empty=True),
                              UniqueUsername())
    password = formencode.validators.PlainText(not_empty=True)
    email = formencode.validators.Email(
        resolve_domain=False, not_empty=True)
    surname = formencode.validators.String(not_empty=True)
    lastname = formencode.validators.String(not_empty=True)
    #password =  formencode.validators.String(not_empty = True)
    confirm_password = formencode.validators.String(not_empty=True)
    chained_validators = [
        formencode.validators.FieldsMatch('password', 'confirm_password')
        ]
    phone = formencode.validators.String(not_empty=True)
    street = formencode.validators.String(not_empty=True)
    number = formencode.validators.String(not_empty=True)
    postcode = formencode.validators.String(not_empty=True)
    city = formencode.validators.String(not_empty=True)
    country = formencode.validators.String(not_empty=True)


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


class UsernameExists(validators.FancyValidator):
    """
    check if username exists in database
    if not, raise error
    """
    def _to_python(self, username, state):
        if not User.get_by_username(username):
            raise formencode.Invalid(
                'That username does not exist', username, state)
        return username


class LoginSchema(formencode.Schema):
    allow_extra_fields = True
    username = formencode.validators.PlainText(not_empty=True)
    username = formencode.All(validators.PlainText(not_empty=True),
                              UsernameExists())
    password = formencode.validators.PlainText(not_empty=True)


# formencode schema for user settings ####################################
class UserSettingsSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    surname = formencode.validators.String(not_empty=True)
    lastname = formencode.validators.String(not_empty=True)
    email = formencode.validators.Email(resolve_domain=False,
                                        not_empty=True)
    phone = formencode.validators.String(not_empty=True)
    fax = formencode.validators.String(not_empty=False)
    street = formencode.validators.String(not_empty=False)
    number = formencode.validators.String(not_empty=False)
    city = formencode.validators.String(not_empty=False)
    postcode = formencode.validators.String(not_empty=False)
    country = formencode.validators.String(not_empty=False)


class UserPasswordSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    new_password = formencode.validators.PlainText(not_empty=True)
    confirm_password = formencode.validators.String(not_empty=True)


## formencode schema for user default license
class UserDefaultLicenseSchema(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
