# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

DEBUG = False
#DEBUG = True

if DEBUG:  # pragma: no cover
    import pprint
    pp = pprint.PrettyPrinter(indent=4)


def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///testing.playlistviews.db')
    #DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


def _registerRoutes(config):
    config.add_route('playlist_list', '/playlist/list')
    config.add_route('playlist_view', '/playlist/view/{playlist_id}')
    config.add_route('playlist_edit', '/playlist/edit/{playlist_id}')
    config.add_route('user_login_first', '/sign_in_first')
    config.add_route('not_found', '/not_found')  # for user_view redirect
    #config.add_route('', '/')


class PlaylistViewIntegrationTests(unittest.TestCase):
    """
    We test the views in c3sar.views.playlist.py
    """
    def setUp(self):
        self.dbsession = _initTestingDB()
        self.config = testing.setUp()
        #self.config.include('c3sar')
        self.dbsession.remove()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.dbsession.remove()
        testing.tearDown()

    def _getTargetClass(self):
        from c3sar.models import Playlist
        return Playlist

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

    def _makePlaylist(self,
                      name=u'the playlist name',
                      issuer=1,
                      ):
        return self._getTargetClass()(
            name, issuer
            )

    def _makePlaylist2(self,
                      name=u'the other name',
                      issuer=2,
                      ):
        return self._getTargetClass()(
            name, issuer
            )

    def test_playlist_add_view(self):
        """
        add playlist -- form test
        """
        from c3sar.views.playlist import playlist_add
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        request.POST = MultiDict([(u'name', u'we')])
        result = playlist_add(request)

        # test: form exists
#        self.assertTrue('form' in result, 'form was not seen.')

#        # test: form shows no errors
#        self.assertEquals(result['form'].form.errors, {},
#                          'form showed errors.')

    def test_playlist_add_not_validating(self):
        """
        playlist_add -- without validating the form
        """
        from c3sar.views.playlist import playlist_add
        request = testing.DummyRequest(
            post=MultiDict(
                [(u'name', u'a test playlist')]
                ))
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        #with self.assertRaises(HTTPFound) as cm:

        result = playlist_add(request)

        # test: form exists
#        self.assertTrue('form' in result, 'form was not seen.')
        # test: form is not validated
#        self.assertTrue(result['form'].form.is_validated,
#                        'form expectedly didnt validate.')
#        self.assertTrue(not result['form'].form.validate(),
#                        'form validated unexpectedly.')
        # test: form shows no errors
#        self.assertEquals(result['form'].form.errors,
#                          {'playlist_name': u'Missing value'},
#                          'form didnt show errors as expected.')

    def test_playlist_add_validating(self):
        """
        playlist_add -- validating the form, metadata only

        without a file
        """
        from c3sar.views.playlist import playlist_add
        request = testing.DummyRequest(
            post=MultiDict([(u'name', u'a test playlist')])
            )
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        # with self.assertRaises(HTTPFound) as cm:
        result = playlist_add(request)
            # expect a redirect
            #        self.assertTrue(isinstance(result, HTTPFound),
            #                        "should have been a redirect")
            # ToDo: check for playlist entry in db
        #    print "cm: " + str(cm)

        from c3sar.models import Playlist
        my_playlist = Playlist.get_by_id(u'1')
        print "my_playlist: " + str(my_playlist)
#       self.assertEquals(my_playlist.name, 'a test playlist')

    def test_playlist_list(self):
        """
        playlist_list
        """
        from c3sar.views.playlist import playlist_list

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)
        instance2 = self._makePlaylist2()  # another playlist
        self.dbsession.add(instance2)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        result = playlist_list(request)

        if DEBUG:  # pragma: no cover
            print "result of test_playlist_list"
            pp.pprint(result)

        # check that there are two playlists in list
        self.assertEquals(len(result['playlists']), 2,
                          "wrong number of playlists in list")
