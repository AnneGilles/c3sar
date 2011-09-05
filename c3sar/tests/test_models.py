import unittest
from pyramid.config import Configurator
from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from c3sar.models import initialize_sql
    session = initialize_sql(create_engine('sqlite://'))
    return session

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from c3sar.views.my_view import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['root'].name, 'root')
        self.assertEqual(info['project'], 'c3sar')

    def test_populate(self):
        #from c3sar.views.my_view import my_view
        #request = testing.DummyRequest()
        #info = my_view(request)
        #self.assertEqual(info['root'].name, 'root')
        #self.assertEqual(info['project'], 'c3sar')
        #print user1

        # https://docs.pylonsproject.org/projects/pyramid/current/tutorials/wiki2/tests.html
        # https://github.com/Pylons/pyramid/blob/master/docs/tutorials/wiki2/src/tests/tutorial/tests.py
        pass

# class  InitializeSqlTests(unittest.TestCase):

#     def setUp(self):
#         from c3sar.models import DBSession
        

class UserModelTests(unittest.TestCase):
    
    def setUp(self):
        self.session = _initTestingDB()
        #self.session.remove()
        print type(self.session)
        
    def tearDown(self):
        #print dir(self.session)
        #self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import User
        return User

    def _makeOne(self, 
                 username='SomeUsername', 
                 password='p4ssw0rd',
                 surname='SomeSurname',
                 lastname='SomeLastname',
                 email='some@email.de',
                 email_conf=False,
                 email_conf_code='ABCDEFG'):
        print type(self.session)
        return self._getTargetClass()(username,password,surname,lastname,
                                      email,email_conf,email_conf_code)
    

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.username, 'SomeUsername')
        self.assertEqual(instance.surname, 'SomeSurname')
        self.assertEqual(instance.lastname, 'SomeLastname')
        # password does not reveal real password
        self.assertNotEqual(instance._get_password(), 'p4ssw0rd')
        # password hash is not empty
        self.assertNotEqual(instance._get_password(), '')
        # XXX ToDo: how to test the password !?
        print "the password: " + instance._get_password()
        self.assertEqual(instance.email, 'some@email.de')
        self.assertEqual(instance.email_conf_code, 'ABCDEFG')
        self.assertEqual(instance.email_conf, False, "expected False")

    # def test_acl(self):
    #     instance = self._makeOne()
    #     print "ACLs: " + repr(instance.__acl__())
# XXX ToDo: how to test the models ACLs?
# http://markmail.org/message/a2xii23tgktw67py has an answer

    def test_get_by_username(self):
        instance = self._makeOne()
#        from c3sar.models import User
#        foo = User.get_by_username('SomeUsername')
#        print "foo is: " + repr(foo)
#        print "type of foo: " + str(type(foo))
#        assertIsInstance(foo, User)
#        print get_by_username(User, 'SomeUsername')
        print type(instance)

class EmailAddressModelTests(unittest.TestCase):
    
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        #print dir(self.session)
        #self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import EmailAddress
        return EmailAddress

    def _makeOne(self, 
                 email_address='test@shri.de'):
        return self._getTargetClass()(email_address)
    

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.email_address, 'test@shri.de')
        self.assertEqual(instance.__repr__(), "<Address('test@shri.de')>")
        #print "repr: " + instance.__repr__()


class PhoneNumberModelTests(unittest.TestCase):
    
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        #print dir(self.session)
        #self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import PhoneNumber
        return PhoneNumber

    def _makeOne(self, 
                 phone_number='06421-98300422'):
        return self._getTargetClass()(phone_number)
    

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.phone_number, '06421-98300422')
        self.assertEqual(instance.__repr__(), "<PhoneNumber('06421-98300422')>")
        #print "repr: " + instance.__repr__()

