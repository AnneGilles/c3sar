# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

DEBUG = True

if DEBUG:  # pragma: no cover
    import pprint
    pp = pprint.PrettyPrinter(indent=4)


def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///testing.bandviews.db')
    #DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


def _registerRoutes(config):
    config.add_route('band_view', '/band/view{band_id}')
    # config.add_route('user_login_first', '/sign_in_first')
    config.add_route('not_found', '/not_found')  # for band_view redirect
    # config.add_route('', '/')


class BandViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.band.py
    """
    def setUp(self):
        self.dbsession = _initTestingDB()
        self.config = testing.setUp()
        #self.config.include('pyramid_mailer.testing')
        self.config.include('c3sar')
        self.dbsession.remove()

    def tearDown(self):
        import transaction
        transaction.abort()
        #self.session.remove()
        testing.tearDown()

    def _getTargetClass(self):
        from c3sar.models import Band
        return Band

    def _getUserClass(self):
        from c3sar.models import User
        return User

    def _makeBand1(self,
                   bandname=u'firstBandname',
                   bandemail=u'band1@example.com',
                   homepage=u'http://band1.example.com',
                   registrar=u'firstUsername',
                   registrar_id=1,
                   ):
        return self._getTargetClass()(
            bandname, bandemail, homepage, registrar, registrar_id)

    def _makeBand2(self,
                   bandname=u'secondBandname',
                   bandemail=u'band2@example.com',
                   homepage=u'http://band2.example.com',
                   registrar=u'secondUsername',
                   registrar_id=2,
                   ):
        return self._getTargetClass()(
            bandname, bandemail, homepage, registrar, registrar_id)

    def _makeUser(self,
                  username=u'firstUsername', surname=u'firstSurname',
                  lastname=u'firstLastname', password=u'password',
                  email=u'first1@shri.de',
                  email_confirmation_code=u'barfbarf',
                  email_is_confirmed=True,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        return self._getUserClass()(
            username, password, surname, lastname,
            email, email_is_confirmed, email_confirmation_code,
            phone, fax)

    def _makeUser2(self,
                  username=u'secondUsername', surname=u'secondSurname',
                  lastname=u'secondLastname', password=u'password',
                  email=u'second2@shri.de',
                  email_confirmation_code=u'barfbarf',
                  email_is_confirmed=False,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        return self._getTargetClass()(
            username, password, surname, lastname,
            email, email_is_confirmed, email_confirmation_code,
            phone, fax)

    def test_band_add_view(self):
        """
        add a band -- form test
        """
        from c3sar.views.band import band_add
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = band_add(request)
        self.assertTrue('form' in result, 'form was not seen.')
        self.assertTrue('viewer_username' in result,
                        'viewer_username was not seen.')

    def test_band_add_view_non_validating(self):
        """
        add a band -- not validating
        """
        from c3sar.views.band import band_add
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'band_name': u'',
                  'band_homepage': u'',
                  'band_email': u'',
                  })
        self.config = testing.setUp(request=request)
        result = band_add(request)
        self.assertTrue('form' in result, 'form was not seen.')
        self.assertTrue('viewer_username' in result,
                        'viewer_username was not seen.')
        self.assertEquals(result['form'].form.errors,
                          {'band_name': u'Please enter a value',
                           'band_email': u'Please enter an email address'},
                          "not the expected error messages")
        self.assertEquals(result['form'].form.validate(),
                          False,
                          "form validated unexpectedly!")

    def test_band_add_view_validating(self):
        """
        add a band -- not validating
        """
        from c3sar.views.band import band_add
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'band_name': u'testband',
                  'band_homepage': u'http://testba.nd',
                  'band_email': u'testband@example.com',
                  'registrar_is_member': '1',
                  })
        request.user = self._makeUser()
        self.config = testing.setUp(request=request)
        result = band_add(request)
        #pp.pprint(result)
        self.assertTrue(isinstance(result, HTTPFound),
                        "expected redirect not seen")
        from c3sar.models import Band
        test_band = Band.get_by_band_id(1)
        self.assertEquals(test_band.id, 1)
        self.assertEquals(test_band.name, 'testband')
        self.assertEquals(test_band.homepage, 'http://testba.nd')
        self.assertEquals(test_band.registrar_id, None)  # no real user :-/
        self.assertEquals(test_band.registrar, 'firstUsername')

    def test_band_view_None(self):
        """
        view a band -- None if none exists
        """
        from c3sar.views.band import band_view
        request = testing.DummyRequest()
        request.matchdict['band_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_view(request)
        # test: redirect
        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('not_found' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/not_found'),
                          "not the redirect expected")

    def test_band_view_one(self):
        """
        view a band - just one
        """
        from c3sar.views.band import band_view
        band_instance = self._makeBand1()
        self.dbsession.add(band_instance)

        request = testing.DummyRequest()
        request.matchdict['band_id'] = 1
        self.config = testing.setUp(request=request)
        result = band_view(request)
        self.assertTrue('band' in result, 'band was not seen.')
        self.assertTrue(result['prev_id'] is 1, 'wrong nav id.')
        self.assertTrue(result['next_id'] is 1, 'wrong nav id.')
        self.assertTrue('viewer_username' in result,
                        'viewer_username was not seen.')
        self.assertTrue(result['viewer_username'] is None,
                        'viewer_username was not seen.')

    def test_band_view_two(self):
        """
        view a band - two bands
        """
        from c3sar.views.band import band_view
        band_instance1 = self._makeBand1()
        self.dbsession.add(band_instance1)
        band_instance2 = self._makeBand2()
        self.dbsession.add(band_instance2)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['band_id'] = 2
        self.config = testing.setUp(request=request)
        result = band_view(request)
        self.assertTrue('band' in result, 'band was not seen.')
        self.assertTrue(result['prev_id'] is 1, 'wrong nav id.')
        self.assertTrue(result['next_id'] is 1, 'wrong nav id.')
        self.assertTrue('viewer_username' in result,
                        'viewer_username was not seen.')
        self.assertTrue(result['viewer_username'] is None,
                        'viewer_username was not seen.')

    def test_band_edit_None(self):
        """
        edit a band -- redirect if id not exists
        """
        from c3sar.views.band import band_edit
        request = testing.DummyRequest()
        request.matchdict['band_id'] = 12      # <---- non-existand id
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_edit(request)
        # test: redirect
        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('not_found' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/not_found'),
                          "not the redirect expected")

    def test_band_edit(self):
        """
        edit a band
        """
        from c3sar.views.band import band_edit
        band_instance = self._makeBand1()
        self.dbsession.add(band_instance)
        self.dbsession.flush()
        request = testing.DummyRequest()
        request.matchdict['band_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_edit(request)
        # test: form
        self.assertTrue('form' in result, "expected form not seen")
        # test: form has values from db
        self.assertEquals(result['form'].form.data,
                          {'homepage': u'http://band1.example.com',
                           'name': u'firstBandname',
                           'email': u'band1@example.com'})
