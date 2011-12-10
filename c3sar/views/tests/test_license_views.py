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
    engine = create_engine('sqlite:///testing.licenseviews.db')
    #DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession  # returns a ScopedSession
    # where DBSession() would return a Session


def _registerRoutes(config):
    config.add_route('band_view', '/band/view/{band_id}')
    # config.add_route('user_login_first', '/sign_in_first')
    config.add_route('not_found', '/not_found')  # for band_view redirect
    # config.add_route('', '/')


class LicenseViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.license.py
    """
    def setUp(self):
        self.dbsession = _initTestingDB()
        # print "dbsession: " + str(type(self.dbsession))
        # dbsession: <class 'sqlalchemy.orm.scoping.ScopedSession'>
        self.config = testing.setUp()
        self.dbsession.remove()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.dbsession.remove()
        testing.tearDown()

    def _getLicenseClass(self):
        from c3sar.models import License
        return License

    def _getUserClass(self):
        from c3sar.models import User
        return User

    def _makeLicense1(self,
                   name=u'firstBandname',
                   uri=u'band1@example.com',
                   img=u'http://band1.example.com',
                   author=u'firstUsername',
                   ):
        return self._getLicenseClass()(
            name, uri, img, author)

    # the tests

    def test_license_introduction(self):
        """
        a general introduction to creative commons licenses
        this view is for people looking at the following
        URL: /license/
        """
        from c3sar.views.license import license
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        result = license(request)

        if DEBUG:  # pragma: no cover
            print "license (introductory view):"
            pp.pprint(result)

        self.assertEquals(result, {'foo': 'bar'})

    def test_license_view(self):
        """view a license -- listing for ONE license"""
        from c3sar.views.license import license_view
        license_1 = self._makeLicense1()                  # make a license
        self.dbsession.add(license_1)
        self.dbsession.flush()

        from c3sar.views.license import license_view
        request = testing.DummyRequest()
        request.matchdict['license_id'] = license_1.id
        self.config = testing.setUp(request=request)

        result = license_view(request)

        if DEBUG:
            print "license view:"
            print "the_license.id: " + str(license_1.id)
            print(result)

        self.assertEquals(license_1.id, 1)
