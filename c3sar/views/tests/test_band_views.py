# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

#DEBUG = True
DEBUG = False

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
    config.add_route('band_view', '/band/view/{band_id}')
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
        add a band -- validating, be redirected to band_view
        """
        from c3sar.views.band import band_add
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'band_name': u'testband',
                  'band_homepage': u'http://testba.nd',
                  'band_email': u'testband@example.com',
                  'registrar_is_member': '1',
                  })
        request.user = self._makeUser()  # a user to add the band
        request.user.username = u"newUser"
        self.dbsession.add(request.user)
        self.dbsession.flush()
        the_user_id = request.user.id

        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_add(request)

        self.assertTrue(isinstance(result, HTTPFound),
                        "expected redirect not seen")
        # check database contents
        from c3sar.models import Band
        max_band_id = Band.get_max_id()
        test_band = Band.get_by_band_id(max_band_id)
        self.assertEquals(test_band.id, max_band_id)
        self.assertEquals(test_band.name, 'testband')
        self.assertEquals(test_band.homepage, 'http://testba.nd')
        self.assertEquals(test_band.registrar_id, the_user_id)  # no real user :-/
        self.assertEquals(test_band.registrar, 'newUser')

    def test_band_view_None(self):
        """
        view a band -- None if none exists. redirect to not_found
        """
        from c3sar.views.band import band_view
        request = testing.DummyRequest()
        request.matchdict['band_id'] = 123456  # high id, RLY
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
        self.dbsession.flush()
        the_id = band_instance.id  # db id of that band
        from c3sar.models import Band
        max_id = Band.get_max_id()

        request = testing.DummyRequest()
        request.matchdict['band_id'] = the_id
        self.config = testing.setUp(request=request)
        result = band_view(request)
        self.assertTrue('band' in result, 'band was not seen.')
        self.assertTrue(
            result['prev_id'] is the_id - 1 or max_id,
            'wrong nav id.')
        self.assertTrue(
            result['next_id'] is the_id + 1 or 1,
            'wrong nav id.')
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

    def test_band_view_two(self):
        """
        view a band - three bands: test next/previous navigation
        """
        from c3sar.views.band import band_view
        band_instance1 = self._makeBand1()
        self.dbsession.add(band_instance1)
        band_instance2 = self._makeBand2()
        self.dbsession.add(band_instance2)
        band_instance3 = self._makeBand1()
        self.dbsession.add(band_instance3)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['band_id'] = 2
        self.config = testing.setUp(request=request)
        result = band_view(request)
        self.assertTrue('band' in result, 'band was not seen.')
        self.assertTrue(result['prev_id'] is 1, 'wrong nav id.')
        self.assertTrue(result['next_id'] is 3, 'wrong nav id.')
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

    def test_band_edit_get(self):
        """
        edit a band -- get stored values into edit form
        """
        from c3sar.views.band import band_edit
        band_instance = self._makeBand1()
        self.dbsession.add(band_instance)
        self.dbsession.flush()
        the_id = band_instance.id  # the id of the band just created
        request = testing.DummyRequest()
        request.matchdict['band_id'] = the_id
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

    def test_band_edit_submit(self):
        """
        edit a band -- re-submit changed values in edit form
        """
        from c3sar.views.band import band_edit

        # put some instance into database
        band_instance = self._makeBand1()
        self.dbsession.add(band_instance)
        self.dbsession.flush()

        # submit some other values: com --> ORG
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'homepage': u'http://band1.example.ORG',
                  'name': u'firstBandnameCHANGED',
                  'email': u'band1@example.ORG'})
        request.matchdict['band_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_edit(request)
        #pp.pprint(result)
        # test: redirect to band/view/1
        self.assertTrue(isinstance(result, HTTPFound),
                        "expected redirect not seen")
        self.assertTrue('band/view/1' in result.headerlist[2][1])
        #print(result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/band/view/1'),
                          "not the redirect expected")

        from c3sar.models import Band
        db_band = Band.get_by_band_id(1)
        # test changed values in db?
        self.assertEquals(db_band.homepage, u'http://band1.example.ORG',
                          "changed value didn't make it to database!?")
        self.assertEquals(db_band.name, u'firstBandnameCHANGED',
                          "changed value didn't make it to database!?")
        self.assertEquals(db_band.email, u'band1@example.ORG',
                          "changed value didn't make it to database!?")

    def test_band_edit_submit_non_validating(self):
        """
        edit a band -- submit non-validating data
        """
        from c3sar.views.band import band_edit

        # put some instance into database
        band_instance = self._makeBand1()
        self.dbsession.add(band_instance)
        self.dbsession.flush()

        # submit some other values: com --> ORG
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'homepage': u'',         # this one is not validated anyways
                  'name': u'',             # will raise validation error
                  'email': u'invalid@email'})  # will raise error, too
        request.matchdict['band_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = band_edit(request)
        #pp.pprint(result['form'].form.errors)
        self.assertEquals(
            result['form'].form.errors,
            {'email': u'The domain portion of the email address is invalid '
             '(the portion after the @: email)',
             'name': u'Please enter a value'},
            "not the expected error messages")
        self.assertEquals(result['form'].form.validate(),
                          False,
                          "form validated unexpectedly!")

    def test_track_list(self):
        """
        track_list

        get number of bands from db, add two,
        check view and confirm resulting number
        """
        from c3sar.models import Band
        band_count = Band.get_max_id()  # how many in db?
        from c3sar.views.band import band_list

        instance1 = self._makeBand1()  # add a band
        self.dbsession.add(instance1)
        instance2 = self._makeBand2()  # add another band
        self.dbsession.add(instance2)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        result = band_list(request)

        if DEBUG:  # pragma: no cover
            print "result of test_band_list"
            pp.pprint(result)

        # check that there are two bandss in list
        self.assertEquals(len(result['bands']), band_count + 2,
                          "wrong number of bands in list")
