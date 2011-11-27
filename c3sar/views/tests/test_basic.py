import unittest

from pyramid import testing


def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    session = DBSession()
    session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def _registerRoutes(config):
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('listen', '/listen')


def _registerCommonTemplates(config):
    config.testing_add_renderer('templates/main.pt')
    config.testing_add_renderer('templates/about.pt')
    config.testing_add_renderer('templates/listen.pt')


class BasicViewTests(unittest.TestCase):
    """
    test the views in c3sar.views.basic.py
    """
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def test_home_view(self):
        from c3sar.views.basic import home_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        result = home_view(request)
        #print "ergebnis :" + str(dir(result))
        #print "ergebnis typ:" + str(type(result))
        #print "ergebnis.items() :" + str(result.items())
        self.assertTrue(
            'Basic Functionality' in result.body, "text not found")

    def test_listen_view(self):
        from c3sar.views.basic import listen_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        listen_view(request)

    def test_about_view(self):
        from c3sar.views.basic import about_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        about_view(request)

    def test_notfound_view(self):
        from c3sar.views.basic import notfound_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        context = "/foo"
        result = notfound_view(context, request)
        #print "result of notfound_view: " + str(result)
        self.assertEquals(str(result), "It aint there, stop trying!")

    def test_not_found_view(self):
        from c3sar.views.basic import not_found_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        #context = "/foo"
        not_found_view(request)

    def test_favicon_view(self):
        from c3sar.views.basic import favicon_view
        request = testing.DummyRequest()
        result = favicon_view(request)
        self.assertEquals(result.content_type, 'image/x-icon',
                          "wrong content-type for favicon!")
        self.assertEquals(len(result.body), 2238,
                          "size \not \equals 2238, favicon filesize changed!?")

    def test_not_implemented_view(self):
        from c3sar.views.basic import not_implemented_view
        _registerCommonTemplates(self.config)
        request = testing.DummyRequest()
        not_implemented_view(request)
