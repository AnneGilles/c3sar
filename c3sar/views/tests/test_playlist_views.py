# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

#DEBUG = False
DEBUG = True

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


from pyramid.decorator import reify
from pyramid.security import unauthenticated_userid


class DummyReqWithUserAttr(testing.DummyRequest):
    """
    extend testing.DummyRequest to carry a 'user' attribute

    used in test_playlist_add_validating,
    """

    @reify
    def user(self):
        from c3sar.models import User
        user = User.get_by_user_id(1)
        return user


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

    def _makeUser(self,
                  username=u'firstUsername', surname=u'firstSurname',
                  lastname=u'firstLastname', password=u'password',
                  email=u'first1@shri.de',
                  email_confirmation_code=u'barfbarf',
                  email_is_confirmed=True,
                  phone=u'+49 6421 968300422',
                  fax=u'+49 6421 690 6996'
                  ):
        '''create a user to be used e.g. when adding a playlist'''
        from c3sar.models import User
        a_user = User(
            username, password, surname, lastname,
            email, email_is_confirmed, email_confirmation_code,
            phone, fax)
        self.dbsession.add(a_user)
        self.dbsession.flush()
        #print a_user.id
        return a_user

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
        self.assertTrue('form' in result, 'form was not seen.')

        # test: form shows no errors
#        self.assertEquals(result['form'].form.errors, {},
#                          'form showed errors.')
        #print("===== result['form']")
        #pp.pprint(result['form'])

    def test_playlist_add_not_validating(self):
        """
        playlist_add -- without validating the form

        check for error message in form
        """
        from c3sar.views.playlist import playlist_add
        request = testing.DummyRequest(
            post=MultiDict(
                [(u'name', u'')]
                ))
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        #with self.assertRaises(HTTPFound) as cm:

        result = playlist_add(request)

        #print "result of test_playlist_add_not_validating"
        #print result

        self.assertEquals(
            result['form'].errors,
            {'name': [u'Field must be between 1 and 30 characters long.']},
            "not the redirect expected")

    def test_playlist_add_validating(self):
        """
        playlist_add -- validating the form, creating db entry

        check db entry to see if it was created
        """
        from c3sar.views.playlist import playlist_add
        a_user = self._makeUser()
        request = DummyReqWithUserAttr(
            post=MultiDict([(u'name', u'a special test playlist')])
            )
        #request.POST = MultiDict([(u'name', u'a special test playlist')])
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)

        #
        result = playlist_add(request)

        # result.headers:
        # ResponseHeaders([
        #     ('Content-Type', 'text/html; charset=UTF-8'),
        #     ('Content-Length', '0'),
        #     ('Location', 'http://example.com/playlist/view/1')])

        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('playlist/view' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/playlist/view/1'),
                          "not the redirect expected")
        # check db
        from c3sar.models import Playlist
        my_playlist = Playlist.get_by_id(1)
        #print "my_playlist: " + str(my_playlist)
        self.assertEquals(my_playlist.name, 'a special test playlist')
        self.assertEquals(my_playlist.issuer, 1)

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

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_list"
        #    pp.pprint(result)

        # check that there are two playlists in list
        self.assertEquals(len(result['playlists']), 2,
                          "wrong number of playlists in list")

    def test_playlist_view_first(self):
        """
        playlist_view, looking at first playlist
        """
        from c3sar.views.playlist import playlist_view

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)
        instance2 = self._makePlaylist2()  # another playlist
        self.dbsession.add(instance2)
        self.dbsession.flush()
        the_id = instance1.id
        from c3sar.models import Playlist
        max_id = Playlist.get_max_id

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        request.matchdict['playlist_id'] = 1

        result = playlist_view(request)

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_view_first"
        #    pp.pprint(result)

        self.assertTrue('playlist' in result, 'playlist was not seen.')
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

    def test_playlist_view_second(self):
        """
        playlist_view, looking at second

        check next_id & prev_id
        """
        from c3sar.views.playlist import playlist_view

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)
        instance2 = self._makePlaylist2()  # another playlist
        self.dbsession.add(instance2)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        request.matchdict['playlist_id'] = 2

        result = playlist_view(request)

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_view_second"
        #    pp.pprint(result)
        # {   'next_id': 1,
        #     'playlist': <c3sar.models.Playlist object at 0x1d8cbb0>,
        #     'prev_id': 1,
        #     'viewer_username': None}
        self.assertEquals(result['next_id'], 1)
        self.assertEquals(result['prev_id'], 1)
        self.assertTrue('playlist' in result)

    def test_playlist_view_nonexistant(self):
        """
        playlist_view, nonexistant playlist_id

        check redirect to not_found view
        """
        from c3sar.views.playlist import playlist_view

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        request.matchdict['playlist_id'] = 123

        result = playlist_view(request)

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_view_nonexistant"
        #    pp.pprint(result)

        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('not_found' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/not_found'),
                          "not the redirect expected")

    def test_playlist_edit_form(self):
        """
        playlist_edit, form test, no submission

        check form
        """
        from c3sar.views.playlist import playlist_edit

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        request.matchdict['playlist_id'] = 1

        result = playlist_edit(request)
        #pp.pprint((result))

        # chack for the right string in the forms html
        self.assertTrue('the playlist name' in str(result))

    def test_playlist_edit_first(self):
        """
        playlist_edit, editing first playlist

        check db for correct change
        """
        from c3sar.views.playlist import playlist_edit

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)

        request = testing.DummyRequest(
            post={
                u'name': u'changed',
                u'submit': True,
                u'_LOCALE_': u'en',
                }
            )
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        request.matchdict['playlist_id'] = 1

        result = playlist_edit(request)

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_edit_first"
        #    pp.pprint(result)
        #pp.pprint(dir(result['form']))
        # self.assertTrue('form' in result)
        # no form: redirect to playlist_view

        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('playlist/view' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/playlist/view/1'),
                          "not the redirect expected")

        # check db
        from c3sar.models import Playlist
        my_playlist = Playlist.get_by_id(1)
        #print "my_playlist: " + str(my_playlist)
        self.assertEquals(my_playlist.name, 'changed')

    def test_playlist_edit_nonvalidating(self):
        """
        playlist_edit, make the form validation fail, check validation errors
        """
        from c3sar.views.playlist import playlist_edit

        instance1 = self._makePlaylist()  # a playlist
        self.dbsession.add(instance1)
        instance2 = self._makePlaylist2()  # another playlist
        self.dbsession.add(instance2)

        request = testing.DummyRequest(
            post={
                u'name': "",
                u'submit': True,
                })
        self.config = testing.setUp(request=request)
        request.matchdict['playlist_id'] = 1

        result = playlist_edit(request)

        #if DEBUG:  # pragma: no cover
        #    print "result of test_playlist_edit_nonvalidating"
        #    pp.pprint(result)
        self.assertTrue('form' in result)
        #print("===== result['form']")
        #pp.pprint(result['form'])
        #pp.pprint(dir(result['form']))

        # XXX check for form errors
        self.assertTrue('errorLi' in str(result['form']))
        self.assertTrue('There was a problem with your submission'
                        in str(result['form']))

    def test_playlist_edit_nonexistant(self):
        """
        playlist_edit, try editing nonexistant playlist
        """
        from c3sar.views.playlist import playlist_edit

        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        request.matchdict['playlist_id'] = 1234

        result = playlist_edit(request)

        self.assertTrue(isinstance(result, HTTPFound), "expected redirect")
        self.assertTrue('not_found' in result.headerlist[2][1])
        self.assertEquals(result.headerlist.pop(),
                          ('Location', 'http://example.com/not_found'),
                          "not the redirect expected")
