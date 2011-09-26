import unittest
import pprint
from pyramid import testing

def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://testing.userviews.db')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

def _registerRoutes(config):
    config.add_route('register', '/register')


class UserViewIntegrationTests(unittest.TestCase):

    def setUp(self):
        #self.session = _initTestingDB()
        import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')

    def tearDown(self):
        #self.session.remove()
        testing.tearDown()

    # def _getTargetClass(self):
    #     from c3sar.models import User
    #     return User

    # def _makeOne(self, name


    def test_home_view(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        # mailer = get_mailer(request)
        result = user_register(request)
        # print "dir(result): " + str(dir(result))
        # print "type(result): " + str(type(result))
        # print "type(result.items): " + str(type(result.items))
        # print "dir(result.items): " + str(dir(result.items))
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        #self.assertEqual(result.status, '200 OK')
        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)
        
        
    def test_user_add_view(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        # mailer = get_mailer(request)
        result = user_register(request)
        # print "dir(result): " + str(dir(result))
        # print "type(result): " + str(type(result))
        # print "type(result.items): " + str(type(result.items))
        # print "dir(result.items): " + str(dir(result.items))
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        #self.assertEqual(result.status, '200 OK')
        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)

    def test_user_confirm_email_view(self):
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        # mailer = get_mailer(request)
        result = user_confirm_email(request)
        # print "dir(result): " + str(dir(result))
        # print "type(result): " + str(type(result))
        # print "type(result.items): " + str(type(result.items))
        # print "dir(result.items): " + str(dir(result.items))
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        #self.assertEqual(result.status, '200 OK')
#        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)


class BasicViewIntegrationTests(unittest.TestCase):

    def setUp(self):
        #self.session = _initTestingDB()
        import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')

    def tearDown(self):
        #self.session.remove()
        testing.tearDown()

    # def _getTargetClass(self):
    #     from c3sar.models import User
    #     return User

    # def _makeOne(self, name


    def test_home_view(self):
        from c3sar.views.basic import home_view
        from c3sar.models import DBSession
        dbsession = DBSession()
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = home_view(request)
        # print "dir(result): " + str(dir(result))
        # print "type(result): " + str(type(result))
        # print "type(result.items): " + str(type(result.items))
        # print "dir(result.items): " + str(dir(result.items))
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        #self.assertEqual(result.status, '200 OK')
        #        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')
        
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)
        