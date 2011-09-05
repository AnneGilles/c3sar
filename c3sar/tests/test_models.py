import unittest
from pyramid.config import Configurator
from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from c3sar.models import DBSession
    from c3sar.models import Base
    from c3sar.models import initialize_sql
    engine = create_engine('sqlite:///:memory:')
#    session = initialize_sql(create_engine('sqlite://'))
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

# class TestMyView(unittest.TestCase):
#     def setUp(self):
#         self.config = testing.setUp()
#         _initTestingDB()

#     def tearDown(self):
#         testing.tearDown()

#     def test_it(self):
#         from c3sar.views.my_view import my_view
#         request = testing.DummyRequest()
#         info = my_view(request)
#         self.assertEqual(info['root'].name, 'root')
#         self.assertEqual(info['project'], 'c3sar')

#     def test_populate(self):
#         #from c3sar.views.my_view import my_view
#         #request = testing.DummyRequest()
#         #info = my_view(request)
#         #self.assertEqual(info['root'].name, 'root')
#         #self.assertEqual(info['project'], 'c3sar')
#         #print user1

#         # https://docs.pylonsproject.org/projects/pyramid/current/tutorials/wiki2/tests.html
#         # https://github.com/Pylons/pyramid/blob/master/docs/tutorials/wiki2/src/tests/tutorial/tests.py
#         pass

# class  InitializeSqlTests(unittest.TestCase):

#     def setUp(self):
#         from c3sar.models import DBSession
        

class UserModelTests(unittest.TestCase):
    
    def setUp(self):
        self.session = _initTestingDB()
#        self.session.remove()
#        print "setUp(): type(self.session): " + str(type(self.session))
#        print "setUp(): dir(self.session): " + str(dir(self.session))
        
    def tearDown(self):
        #print dir(self.session)
        self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import User
        return User

    def _makeOne(self, 
                 username=u'SomeUsername', 
                 password=u'p4ssw0rd',
                 surname=u'SomeSurname',
                 lastname=u'SomeLastname',
                 email=u'some@email.de',
                 email_conf=False,
                 email_conf_code=u'ABCDEFG'):
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

    def off_test_ACLs(self):
        import webtest
        from pyramid.exceptions import Forbidden
        from c3sar import main

        app = webtest.TestApp(main({}, **{'sqlalchemy.url': 'sqlite://'}))

        url = '/user/edit/2'
        # Make sure the view is not visible to the public
        self.assertRaises(Forbidden, app.get, url)


    def test_get_by_username(self):
        instance = self._makeOne()
        from c3sar.models import User
        print str(User.get_by_username('SomeUsername'))
        foo = User.get_by_username('SomeUsername')
        print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(foo.username, 'SomeUsername')

    def off_test_get_by_user_id(self):
        instance = self._makeOne()
        from c3sar.models import User
        foo = User.get_by_user_id('1')
        self.assertEqual(instance.username, 'SomeUsername')
        self.assertEqual(foo.username, 'SomeUsername')

    def off_test_check_password(self):
        instance = self._makeOne()
        from c3sar.models import User
        result = User.check_password('SomeUsername', instance.password)

        self.assertTrue(result, "result was not True")



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



## ideas for testing 'main', or at least having it covered: 
# http://groups.google.com/group/pylons-devel/browse_thread/thread/e12a4dd55917c079
