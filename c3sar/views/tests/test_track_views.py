# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

DEBUG = False
#DEBUG = True

if DEBUG:  # pragma: no cover
    import pprint
    pp = pprint.PrettyPrinter(indent=4)


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

    def _makeTrack3(self,
                    name=u'yet another track name',
                    album=u'yet another album',
                    url=u"http://yet_another_track.yet_another_album.com",
                    filepath=u"yet_another_song.mp3",
                    bytesize=u"321654"
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

    def test_track_add_validating_w_file(self):
        """
        track_add -- validating the form, metadata & file
        """
        from c3sar.views.track import track_add

        # note: file upload is a FieldStorage thing
        # # request.POST looks like this:
        # MultiDict(
        #     [
        #      (u'_csrf', u'fe0251aad0b051c0bfc856826ff50b2fe917c8ac'),
        #      (u'track_name', u'another track'),
        #      (u'track_album', u'another album'),
        #      (u'track_url', u'http://somewhe.re/track.mp3'),
        #      (u'track_file',
        #        FieldStorage(
        #           u'track_file', u"lissie_-_when_i'm_alone.mp3")),
        #      (u'form.submitted', u'Save')])
        #
        class AFile(object):
            """dummy to allow for attributes """
            pass
        _a_file = AFile()
        _a_file.file = open('c3sar/models.py', 'r')
        _a_file.filename = 'my model'
        import os
        _a_file.size = os.path.getsize('c3sar/models.py')

        request = testing.DummyRequest(
            post={u'form.submitted': True,
                  u'track_name': u'my test track',
                  u'track_upload': _a_file,  # see class AFile above
                  u'track_url': u'http://me.com/file.mp3',
                  u'track_album': u'my test album',
                  })
        if DEBUG:  # pragma: no cover
            print "the request.POST: "
            pp.pprint(request.POST)

        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_add(request)
        if DEBUG:  # pragma: no cover
            print "the result of track_add with file: "
            pp.pprint(result)

        # close the file again
        _a_file.file.close()

        # expect a redirect
        self.assertTrue(isinstance(result, HTTPFound),
                        "should have been a redirect")
        # ToDo: check for track entry in db
        from c3sar.models import Track
        my_track = Track.get_by_track_id(u'1')
        self.assertEquals(my_track.name, 'my test track')
        self.assertEquals(my_track.album, 'my test album')
        self.assertEquals(my_track.url, 'http://me.com/file.mp3')
        #self.assertEquals(my_track.bytesize, _a_file.size)

        # TODO: remove that SAWarning:
        #       Unicode type received non-unicode bind param value.
        # TODO: how to test upload of file?

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
        self.assertEquals(result['next_id'], 1, "wrong id?")
        self.assertEquals(result['prev_id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")

    def test_track_view_next_prev(self):
        """
        track_view -- check prev/next navigation
        """
        from c3sar.views.track import track_view
        instance = self._makeTrack()  # a track
        self.dbsession.add(instance)
        instance = self._makeTrack2()  # another track
        self.dbsession.add(instance)
        instance = self._makeTrack3()  # yet another track
        self.dbsession.add(instance)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 2
        self.config = testing.setUp(request=request)
        #_registerRoutes(self.config)
        result = track_view(request)

        if DEBUG:  # pragma: no cover
            print "the result of test_track_view: "
            pp.pprint(result)

        self.assertEquals(result['id'], 2, "wrong id?")
        #self.assertEquals(result['license'], 1, "wrong id?")
        self.assertEquals(result['next_id'], 3, "wrong id?")
        self.assertEquals(result['prev_id'], 1, "wrong id?")
        #self.assertEquals(result['id'], 1, "wrong id?")

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

    def test_track_add_license(self):
        """ add license view -- just open it"""
        from c3sar.views.track import track_add_license
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        result = track_add_license(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        self.assertTrue('track' in result, "no track found")

    def test_track_add_license_submit_cc_generic(self):
        """ track add license & submit: cc-by generic"""
        from c3sar.views.track import track_add_license
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest(
            post={'form.submitted': True,
                  u'cc_js_want_cc_license': u'sure',
                  u'cc_js_share': u'1',
                  u'cc_js_remix': u'',
                  u'cc_js_jurisdiction': u'generic',
                  u'cc_js_result_uri':
                      u'http://creativecommons.org/licenses/by/3.0/',
                  u'cc_js_result_img':
                      u'http://i.creativecommons.org/l/by/3.0/88x31.png',
                  u'cc_js_result_name':
                      u'Creative Commons Attribution 3.0 Unported',
                  })
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_add_license(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        # check for redirect
        self.assertTrue(isinstance(result, HTTPFound), "no redirect")
        # redirect goes to track/view/1
        self.assertTrue('track/view/1' in result.headerlist[2][1],
                        "no redirect")

        from c3sar.models import Track
        the_track = Track.get_by_track_id(1)
        the_license = the_track.license[0]
        self.assertEquals(the_license.id, 1,
                          "wrong id: should be the only one in database")
        self.assertEquals(the_license.img,
                          u'http://i.creativecommons.org/l/by/3.0/88x31.png',
                          "wrong license img")
        self.assertEquals(the_license.uri,
                          u'http://creativecommons.org/licenses/by/3.0/',
                          "wrong license uri")
        self.assertEquals(
            the_license.name,
            u'Creative Commons Attribution 3.0 Unported',
            "wrong license name")

        # and now let's go to track/view/1
        from c3sar.views.track import track_view
        request = testing.DummyRequest()
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        result = track_view(request)

    def test_track_add_license_submit_by_nc_sa_de(self):
        """ track add license & submit: cc-by-nc-sa-de"""
        from c3sar.views.track import track_add_license
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest(
            post={'form.submitted': True,
                  u'cc_js_want_cc_license': u'sure',
                  u'cc_js_share': u'1',
                  u'cc_js_remix': u'',
                  u'cc_js_nc': u'1',
                  u'cc_js_jurisdiction': u'de',
                  u'cc_js_result_uri':
                      u'http://creativecommons.org/licenses/by-nc-sa/3.0/',
                  u'cc_js_result_img':
                      u'http://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png',
                  u'cc_js_result_name':
                  u'Creative Commons Attribution-NonCommercial-ShareAlike 3.0',
                  })
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_add_license(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        # check for redirect
        self.assertTrue(isinstance(result, HTTPFound), "no redirect")

        from c3sar.models import Track
        the_track = Track.get_by_track_id(1)
        the_license = the_track.license[0]
        self.assertEquals(the_license.id, 1,
                          "wrong id: should be the only one in database")
        self.assertEquals(
            the_license.img,
            u'http://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png',
            "wrong license image")
        self.assertEquals(
            the_license.uri,
            u'http://creativecommons.org/licenses/by-nc-sa/3.0/',
            "wrong license uri")
        self.assertEquals(
            the_license.name,
            u'Creative Commons Attribution-NonCommercial-ShareAlike 3.0',
            "wrong license name")

    def test_track_add_license_submit_all_rights_reserved(self):
        """ track add license & submit: allrights reserved"""
        from c3sar.views.track import track_add_license
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest(
            post={'form.submitted': True,
                  u'cc_js_want_cc_license': u'nah',
                  u'cc_js_share': u'1',
                  u'cc_js_jurisdiction': u'de',
                  u'cc_js_result_uri': u'',
                  u'cc_js_result_img': u'',
                  u'cc_js_result_name': u'No license chosen',
                  })
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_add_license(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        # check for redirect
        self.assertTrue(isinstance(result, HTTPFound), "no redirect")

        from c3sar.models import Track
        the_track = Track.get_by_track_id(1)
        the_license = the_track.license[0]
        self.assertEquals(the_license.id, 1,
                          "wrong id: should be the only one in database")
        self.assertEquals(the_license.img, u'', "wrong license image")
        self.assertEquals(the_license.uri, u'', "wrong license uri")
        self.assertEquals(the_license.name,
                          u'All rights reserved',
                          "wrong license name")

    def test_track_edit_invalid_id(self):
        """edit track -- supply invalid id"""
        from c3sar.views.track import track_edit
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 12
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_edit(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        # check for redirect
        self.assertTrue(isinstance(result, HTTPFound), "no redirect")

    def test_track_edit_get_values(self):
        """edit track -- supply invalid id"""
        from c3sar.views.track import track_edit
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest()
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_edit(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)

        # check for redirect
        self.assertTrue('form' in result, "no form seen")
        self.assertEquals(
            result['form'].form.data,
            {'album': u'the album',
             'url': u'http://the_track.the_album.com',
             'name': u'the track name'},
            "wrong form values seen")

    def test_track_edit_submit_invalid_values(self):
        """edit track -- supply invalid id"""
        from c3sar.views.track import track_edit
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'name': u''
                })
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_edit(request)

        # check for redirect
        self.assertTrue('form' in result, "no form seen")
        self.assertEquals(
            result['form'].form.errors,
            {'album': u'Missing value',
             'name': u'Please enter a value',
             'url': u'Missing value'})

    def test_track_edit_set_new_values(self):
        """edit track -- submit valid data through form"""
        from c3sar.views.track import track_edit
        # add a track
        track1 = self._makeTrack()
        self.dbsession.add(track1)
        self.dbsession.flush()

        request = testing.DummyRequest(
            post={'form.submitted': True,
                  'name': u"changed track name",
                  'album': u'changed album name',
                  'url': u"http://totally.different.url"}
            )
        request.matchdict['track_id'] = 1
        self.config = testing.setUp(request=request)
        _registerRoutes(self.config)
        result = track_edit(request)

        if DEBUG:  # pragma: no cover
            pp.pprint(result)
            #pp.pprint(result.headers[2])

        # check for redirect
        self.assertTrue(isinstance(result, HTTPFound), "no redirect seen")
        self.assertTrue('track/view/1' in str(result.headers),
                        "wrong redirect seen")
        # compare submitted data with track from database
        from c3sar.models import Track
        db_track = Track.get_by_track_id(1)
        self.assertEquals(db_track.name, u"changed track name",
                          "data mismatch")
        self.assertEquals(db_track.album, u"changed album name",
                          "data mismatch")
        self.assertEquals(db_track.url, u"http://totally.different.url",
                          "data mismatch")
