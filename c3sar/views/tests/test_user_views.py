# -*- coding: utf-8 -*-
import unittest
import pprint
from pyramid import testing

pp = pprint.PrettyPrinter(indent=4)


DEBUG = True

def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://testing.userviews.db')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

class UserViewIntegrationTests(unittest.TestCase):

    def setUp(self):
        #self.session = _initTestingDB()
        import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        from c3sar.models import DBSession, User
        DBSession.remove()

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

        result = user_register(request)

        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')

        if DEBUG:
            print "--- in c3sar.tests.test_user_views.UserViewIntegrationTests.test_home_view()"
            pp.pprint(result)
        
        
    def test_user_add_view(self):
        from c3sar.views.user import user_register
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        # mailer = get_mailer(request)
        result = user_register(request)

        print "the result of test_user_add_view:user_register(request):"
        pp.pprint(result)

        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')

        if DEBUG:
            print "--- in c3sar.tests.test_user_views.UserViewIntegrationTests.test_user_add_view()"
            pp.pprint(result)

    def test_user_confirm_email_view(self):
        """
        a test for the user_email_confirm view
        """
        from c3sar.views.user import user_confirm_email
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        # mock values
        request.matchdict['code'] = 'IDoExist'
        request.matchdict['user_name'] = 'firstUsername'
        request.matchdict['user_email'] = 'some@email.com'
        # mailer = get_mailer(request)

        #print "== DEBUG: ======================"
        #help(user_confirm_email)
        #dir(user_confirm_email)
        #print "== /DEBUG ======================"
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


        if DEBUG:
            print "--- in c3sar.tests.test_user_views.UserViewIntegrationTests.test_user_confirm_email_view()"

            print "=============== results for test_user_confirm_email_view ======"
            pp.pprint(result)
            print "=============== results for test_user_confirm_email_view /end ======"


class BasicViewIntegrationTests(unittest.TestCase):

    def setUp(self):
        """
        This sets up the application registry with the registrations
        your application declares in its ``ìncludeme`` function
        """
        #self.session = _initTestingDB()
        #import c3sar
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        from c3sar.models import DBSession, User
        DBSession.remove()

    def tearDown(self):
        """clear out the application registry"""
        #self.session.remove()
        testing.tearDown()

    # def _getTargetClass(self):
    #     from c3sar.models import User
    #     return User

    # def _makeOne(self, name


    def test_home_view(self):
        from c3sar.views.basic import home_view
        from c3sar.models import DBSession
        dbsession = DBSession
        request = testing.DummyRequest()
        #self.config = testing.setUp(request=request)
        result = home_view(request)
        print " "
        print "dir(result): " + str(dir(result))
        print "type(result): " + str(type(result))
        print "type(result.items): " + str(type(result.items))
        print "dir(result.items): " + str(dir(result.items))
        print "result, prettyprinted: "
        pp.pprint(result)
        # print "help(result.items): " + str(help(result.items))
        # print "result.viewkeys(): " + str(result.viewkeys())
        # print "help(result.viewkeys()): " + str(help(result.viewkeys()))
        #for item in result:
        #    print item
        
        #self.assertEqual(result.status, '200 OK', "not 200 OK")   # Todo
        
        #        self.assertTrue('form' in result.viewkeys(), 'form was not seen.')
        #if DEBUG:
        #    print "--- in c3sar.tests.test_user_views.BasicViewIntegrationTests.test_home_view()"
        
        