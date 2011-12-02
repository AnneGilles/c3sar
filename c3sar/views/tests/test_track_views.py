# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

import pprint
pp = pprint.PrettyPrinter(indent=4)

DEBUG = False


def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///testing.trackviews.db')
    #DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


def _registerRoutes(config):
    config.add_route('track_list', '/track/list')
    config.add_route('track_view', '/track/view/{track_id}')
    config.add_route('user_login_first', '/sign_in_first')
    config.add_route('not_found', '/not_found')  # for user_view redirect
    #config.add_route('', '/')


class TrackViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.track.py
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
        from c3sar.models import Track
        return Track

    # def _makeUser(self,
    #               username=u'firstUsername', surname=u'firstSurname',
    #               lastname=u'firstLastname', password=u'password',
    #               email=u'first1@shri.de',
    #               email_confirmation_code=u'barfbarf',
    #               email_is_confirmed=True,
    #               phone=u'+49 6421 968300422',
    #               fax=u'+49 6421 690 6996'
    #               ):
    #     return self._getTargetClass()(
    #         username, password, surname, lastname,
    #         email, email_is_confirmed, email_confirmation_code,
    #         phone, fax)

    def _makeTrack(self,
                   name=u'the track name',
                   album=u'the album',
                   url=u"http://the_track.the_album.com",
                   filepath=u"mysong.mp3",
                   bytesize=u"123456"
                  ):
        return self._getTargetClass()(
            name, album, url, filepath, bytesize
            )

    def _makeTrack2(self,
                   name=u'the other track name',
                   album=u'the other album',
                   url=u"http://the_other_track.the_other_album.com",
                   filepath=u"my_other_song.mp3",
                   bytesize=u"654321"
                  ):
        return self._getTargetClass()(
            name, album, url, filepath, bytesize
            )

    def test_sanitize_filename(self):
        """
        test sanitize_filename function
        """
        from c3sar.views.track import sanitize_filename

        # spaces are replaced by underscores
        result = sanitize_filename('foo bar')
        self.assertEquals(result, 'foo_bar', 'wrong result')

        # umlauts are deleted
        result = sanitize_filename('fööp')
        self.assertEquals(result, 'fp', 'wrong result')

        # underscores are OK
        result = sanitize_filename('foo_bar')
        self.assertEquals(result, 'foo_bar', 'wrong result')

        # brackets are OK
        result = sanitize_filename('foo(bar).mp3')
        self.assertEquals(result, 'foo(bar).mp3', 'wrong result')

        # dashes are OK
        result = sanitize_filename('foo-bar.mp3')
        self.assertEquals(result, 'foo-bar.mp3', 'wrong result')

        # dots are OK
        result = sanitize_filename('foo.bar.mp3')
        self.assertEquals(result, 'foo.bar.mp3', 'wrong result')

        # numbers are OK
        result = sanitize_filename('foo123.mp3')
        self.assertEquals(result, 'foo123.mp3', 'wrong result')

    def test_track_add_view(self):
        """
        add track -- form test
        """
        from c3sar.views.track import track_add
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        result = track_add(request)

        # test: form exists
        self.assertTrue('form' in result, 'form was not seen.')

        # test: form shows no errors
        self.assertEquals(result['form'].form.errors, {},
                          'form showed errors.')

    def test_track_add_not_validating(self):
        """
        track_add -- without validating the form
        """
        from c3sar.views.track import track_add
        request = testing.DummyRequest(
            post={'form.submitted': True,
                  u'track_url': u'http://me.com/file.mp3',
                  u'track_album': u'my test album',
                  })
        self.config = testing.setUp(request=request)
        result = track_add(request)

        # test: form exists
        self.assertTrue('form' in result, 'form was not seen.')
        # test: form is not validated
        self.assertTrue(result['form'].form.is_validated,
                        'form expectedly didnt validate.')
        self.assertTrue(not result['form'].form.validate(),
                        'form validated unexpectedly.')
        # test: form shows no errors
        self.assertEquals(result['form'].form.errors,
                          {'track_name': u'Missing value'},
                          'form didnt show errors as expected.')

    def test_track_add_validating(self):
        """
        track_add -- validating the form, metadata only

        without a file
        """
        from c3sar.views.track import track_add
        request = testing.DummyRequest(
            post={u'form.submitted': True,
                  u'track_name': u'my test track',
                  #u'track_file': u'', # <-- without file upload!
                  u'track_url': u'http://me.com/file.mp3',
                  u'track_album': u'my test album',
                  })
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_add(request)

        # expect a redirect
        self.assertTrue(isinstance(result, HTTPFound),
                        "should have been a redirect")
        # ToDo: check for track entry in db
        from c3sar.models import Track
        my_track = Track.get_by_track_id(u'1')
        self.assertEquals(my_track.name, 'my test track')
        self.assertEquals(my_track.album, 'my test album')
        self.assertEquals(my_track.url, 'http://me.com/file.mp3')
        # TODO: remove that SAWarning:
        #       Unicode type received non-unicode bind param value.

#    def test_track_add_validating_w_file(self):
#        """
#        track_add -- validating the form, metadata & file
#        """
#        from c3sar.views.track import track_add
#
#        # note: file upload is a FieldStorage thing
#        # request.POST looks like this:
#         MultiDict(
#             [
#                 (u'_csrf', u'fe0251aad0b051c0bfc856826ff50b2fe917c8ac'),
#                 (u'track_name', u'another track'),
#                 (u'track_album', u'another album'),
#                 (u'track_url', u'http://somewhe.re/track.mp3'),
#                 (u'track_file',
#                  FieldStorage(
#                   u'track_file', u"lissie_-_when_i'm_alone.mp3")),
#                 (u'form.submitted', u'Save')])
#
#         from cgi import FieldStorage
#         request = testing.DummyRequest(
#             post={u'form.submitted': True,
#                   u'track_name': u'my test track',
# #                   u'track_file': {
# #                     'file': u'models.py',
# #                     'filename': u'models.py',
# #                     },
# #
# #                   u'track_file': [
# #                     ('filename', u'models.py'),
# #                     #('filename', u'models.py')
# #                     ],
# #
#                   u'track_file': FieldStorage(u'track_file', u'models.py'),
#                   u'track_url': u'http://me.com/file.mp3',
#                   u'track_album': u'my test album',
#                   })
#         self.config = testing.setUp(request=request)
#         _registerRoutes(self.config)
#         result = track_add(request)
#
#         # expect a redirect
#         self.assertTrue(isinstance(result, HTTPFound),
#                         "should have been a redirect")
#         # ToDo: check for track entry in db
#         from c3sar.models import Track
#         my_track = Track.get_by_track_id(u'1')
#         self.assertEquals(my_track.name, 'my test track')
#         self.assertEquals(my_track.album, 'my test album')
#         self.assertEquals(my_track.url, 'http://me.com/file.mp3')
#         # TODO: remove that SAWarning:
#         #       Unicode type received non-unicode bind param value.
#        # TODO: how to test upload of file?

    def test_track_view(self):
        """
        track_view -- look at the file
        """
        from c3sar.views.track import track_view
        instance = self._makeTrack()  # a track
        self.dbsession.add(instance)

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        #_registerRoutes(self.config)
        result = track_view(request)

        if DEBUG:  # pragma: no cover
            print "the result of test_track_view: "
            pp.pprint(result)

        self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['license'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        # expect a redirect
        #self.assertTrue(isinstance(result, HTTPFound),
        #                "should have been a redirect")
        # ToDo: check for track entry in db

    def test_track_view_id_not_found(self):
        """
        track_view -- track id non-existing
        """
        from c3sar.views.track import track_view
        instance = self._makeTrack()  # a track
        self.dbsession.add(instance)

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 5  # <-- not existing
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_view(request)

        if DEBUG:  # pragma: no cover
            print "the result of test_track_view: "
            pp.pprint(result)

        #self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['license'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")
        # expect a redirect
        self.assertTrue(isinstance(result, HTTPFound),
                        "should have been a redirect")
        # ToDo: check for track entry in db

    def test_track_list(self):
        """
        track_list
        """
        from c3sar.views.track import track_list

        instance1 = self._makeTrack()  # a track
        self.dbsession.add(instance1)
        instance2 = self._makeTrack2()  # another track
        self.dbsession.add(instance2)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        result = track_list(request)

        if DEBUG:  # pragma: no cover
            print "result of test_track_list"
            pp.pprint(result)

        # check that there are two tracks in list
        self.assertEquals(len(result['tracks']), 2,
                          "wrong number of tracks in list")
