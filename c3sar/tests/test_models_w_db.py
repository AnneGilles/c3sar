import unittest
from pyramid.config import Configurator
from pyramid import testing
import os

def _initTestingDB():
    from sqlalchemy import create_engine
    from c3sar.models import DBSession
    from c3sar.models import Base

    from c3sar.models import populate
    from sqlalchemy.exc import IntegrityError

    if os.path.isfile('testing.db'):
        # delete existing db
        os.unlink('testing.db')
    engine = create_engine('sqlite:///testing.db')
#    session = initialize_sql(create_engine('sqlite://'))
#    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except Exception, e:
        print str(e)
#        transaction.abort()
    return DBSession


class TestInitializeSql(unittest.TestCase):

    def setUp(self):
        from c3sar.models import DBSession
        DBSession.remove()

    def tearDown(self):
        from c3sar.models import DBSession
        DBSession.remove()
        

    def _callFUT(self, engine):
        from c3sar.models import initialize_sql
        return initialize_sql(engine)
        
    def test_initialize_sql(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        from c3sar.models import User, DBSession
        self.assertEqual(DBSession.query(User).one().username,
            'eins')




class UserModelTests(unittest.TestCase):
    
    def setUp(self):
        self.session = _initTestingDB()
        self.session.close()
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
#        print "type(self.session): " + str(type(self.session))
#        print "dir(self.session): " + str(dir(self.session))
        return self._getTargetClass()(username,password,surname,lastname,
                                      email,email_conf,email_conf_code)
    

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.username, 'SomeUsername', "No match!")
        self.assertEqual(instance.surname, 'SomeSurname', "No match!")
        self.assertEqual(instance.lastname, 'SomeLastname', "No match!")
        # password does not reveal real password
        self.assertNotEqual(instance._get_password(), 'p4ssw0rd', "No match!")
        # password hash is not empty
        self.assertNotEqual(instance._get_password(), '', "No match!")
        #print "result of instance.get_password: " + instance._get_password()
        self.assertEqual(instance.email, 'some@email.de', "No match!")
        self.assertEqual(instance.email_conf_code, 'ABCDEFG', "No match!")
        self.assertEqual(instance.email_conf, False, "expected False")

        #     # def test_acl(self):
        #     #     instance = self._makeOne()
        #     #     print "ACLs: " + repr(instance.__acl__())
        # # XXX ToDo: how to test the models ACLs?
        # # http://markmail.org/message/a2xii23tgktw67py has an answer
        
        #     def off_test_ACLs(self):
        #         import webtest
        #         from pyramid.exceptions import Forbidden
        #         from c3sar import main
        
        #         app = webtest.TestApp(main({}, **{'sqlalchemy.url': 'sqlite://'}))
        
        #         url = '/user/edit/2'
        #         # Make sure the view is not visible to the public
        #         self.assertRaises(Forbidden, app.get, url)
        
    def test_user_listing(self):
        instance = self._makeOne()
        user_cls = self._getTargetClass()
        result = user_cls.user_listing('foo')
        #print "user_cls.user_listing('foo')" + repr(result)

        #result =
#        print help(user_cls.user_listing('foo'))
#       print "dir(user_cls.user_listing('foo'))" + repr(result)


    def test_get_by_username(self):
        instance = self._makeOne()
        #from c3sar.models import User
        myUserClass = self._getTargetClass()
        #print "myUserClass: " +str(myUserClass)
#        print "str(myUserClass.get_by_username('SomeUsername')): " + str(myUserClass.get_by_username('SomeUsername'))
#        foo = myUserClass.get_by_username(instance.username)
#        print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(instance.username, 'SomeUsername')

    def test_get_by_user_id(self):
        instance = self._makeOne()
        from c3sar.models import User
        foo = User.get_by_user_id('1')
        self.assertEqual(instance.username, 'SomeUsername')
        self.assertEqual(foo.username, 'eins')

    def test_check_password(self):
        instance = self._makeOne()
        result = self._getTargetClass().check_password('eins', 'password')
        self.assertTrue(result, "result was not True")

    def test_check_password_False(self):
        result = self._getTargetClass().check_password('nonexistant', 'somepassword')
        self.assertFalse(result, "result was not False")

    def test_check_username_exists(self):
        result = self._getTargetClass().check_username_exists('eins')
        self.assertTrue(result, "result was not True")

    def test_check_username_exists_False(self):
        result = self._getTargetClass().check_username_exists('nonexistant')
        self.assertFalse(result, "result was not False")

    def test_check_user_or_None(self):
        result = self._getTargetClass().check_user_or_None('eins')
        self.assertTrue(result, "result was not True")

    def test_check_user_or_None_None(self):
        result = self._getTargetClass().check_user_or_None('nonexistant')
        #print "result of check_user_or_None('nonexistant'): " +  str(result)
        self.assertEquals(result, None, "result was not None")


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
