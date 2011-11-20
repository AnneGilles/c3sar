import unittest
#from pyramid.config import Configurator
from pyramid import testing
import os

# debugging
#DEBUG = True
DEBUG = False

if DEBUG:
    print "== test_models_w_db.py =="

def _initTestingDB():
    if DEBUG: print "this is _initTestingDB()"
    from sqlalchemy import create_engine
    from c3sar.models import DBSession
    from c3sar.models import Base

    from c3sar.models import populate
    from sqlalchemy.exc import IntegrityError

    if os.path.isfile('testing.db'):
        # delete existing db
        os.unlink('testing.db')
        #print "deleted old database *testing.db*."
    engine = create_engine('sqlite:///testing.db')
#    session = initialize_sql(create_engine('sqlite://'))
#    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    # try:
    #     populate()
    # except Exception, e:
    #     print str(e)
#        transaction.abort()
    return DBSession



class LicenseModelTests(unittest.TestCase):
    if DEBUG: print "----- this is class LicenseModelTests "

    def setUp(self):
        self.session = _initTestingDB()
        self.session.close()

    def tearDown(self):
        self.session.remove()


    def _getTargetClass(self):
        from c3sar.models import License
        return License

    def _makeOne(self,
                 name=u'Some Licensename',
                 url=u'http://creativecommons.org/licenses/by-nc-sa/3.0/',
                 img=u'http://i.creativecommons.org/l/by/3.0/88x31.png',
                 author=u'Some Name',
                 ):
        return self._getTargetClass()(name,url,img,author)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'Some Licensename', "No match!")
        self.assertEqual(instance.uri, 'http://creativecommons.org/licenses/by-nc-sa/3.0/', "No match!")
        self.assertEqual(instance.img, 'http://i.creativecommons.org/l/by/3.0/88x31.png', 'No match!')
        self.assertEqual(instance.author, 'Some Name', "No match!")

    def test_get_by_license_id(self):
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        #print "--- type(instance): " + str(type(instance)) #<class 'c3sar.models.License'>
        #print "--- dir(instance): " + str(dir(instance)) # ... '_sa_instance_state', 'author',
                       # 'get_by_license_id', 'id', 'license_listing', 'metadata', 'name', 'url'
        #print "--- instance.id: " + str(instance.id) # 1
        from c3sar.models import License
        result = License.get_by_license_id(1)
        #print "result: " + str(result) # <c3sar.models.License object at 0x949f74c>
        #print "result.id: " + str(result.id) # 1
        self.assertNotEqual(instance.id, None, "may not be None.")
        self.assertNotEqual(result.id, None, "may not be None.")
        self.assertEqual(instance.id, result.id, "license ids didn't match!")

    def test_license_listing(self):
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        #print "--- type(instance): " + str(type(instance)) #<class 'c3sar.models.License'>
        #print "--- dir(instance): " + str(dir(instance)) # ... '_sa_instance_state', 'author',
                       # 'get_by_license_id', 'id', 'license_listing', 'metadata', 'name', 'url'
        #print "--- instance.id: " + str(instance.id) # 1
        from c3sar.models import License
        result = License.license_listing()
        #print "--- result: " + str(result) # [<c3sar.models.License object at 0x9fba10c>]
        #print "--- dir(result): " + str(dir(result)) #
        #print "--- license_listing: result.__len__(): " + str(result.__len__()) # 1
        self.assertEqual(result.__len__(), 1, "we expect the result list to have one entry")

class TrackModelTests(unittest.TestCase):
    if DEBUG: print "----- this is class TrackModelTests "
    def setUp(self):
        self.session = _initTestingDB()
        self.session.close()

    def tearDown(self):
        self.session.remove()


    def _getTargetClass(self):
        from c3sar.models import Track
        return Track

    def _makeOne(self,
                 name=u'Some Trackname',
                 url=u'http://trackshack.net/track.mp3',
                 album=u'Some Album Name',
                 filepath=None,
                 bytesize=None,
                 ):
        return self._getTargetClass()(name, album, url, filepath, bytesize)

    def test_constructor(self):
        if DEBUG: print "----- this is TrackModelTests.test_constructor"
        instance = self._makeOne()
        #print "track instance.url: " + instance.url
        self.assertEqual(instance.name, 'Some Trackname', "No match!")
        self.assertEqual(instance.url, 'http://trackshack.net/track.mp3', "No match!")
        self.assertEqual(instance.album, 'Some Album Name', "No match!")

    def test_get_by_track_id(self):
        if DEBUG: print "----- this is TrackModelTests.test_get_by_track_id"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        #print "--- type(instance): " + str(type(instance)) #<class 'c3sar.models.License'>
        #print "--- dir(instance): " + str(dir(instance)) # ... '_sa_instance_state', 'author',
                       # 'get_by_license_id', 'id', 'license_listing', 'metadata', 'name', 'url'
        #print "--- instance.id: " + str(instance.id) # 1
        from c3sar.models import Track
        result = Track.get_by_track_id(1)
        #print "result: " + str(result) # <c3sar.models.Track object at 0x949f74c>
        #print "result.id: " + str(result.id) # 1
        self.assertNotEqual(instance.id, None, "may not be None.")
        self.assertNotEqual(result.id, None, "may not be None.")
        self.assertEqual(instance.id, result.id, "track ids didn't match!")

    def test_get_by_track_name(self):
        """
        testing Track.get_by_track_name()
        """
        if DEBUG: print "----- this is TrackModelTests.test_get_by_track_name"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        #print "--- type(instance): " + str(type(instance)) #<class 'c3sar.models.Track'>
        #print "--- instance.id: " + str(instance.id) # 1
        from c3sar.models import Track
        result = Track.get_by_track_name(u'Some Trackname')
        self.assertEqual(instance.name, result.name, "should have matched.")
        self.assertEqual(instance.id, result.id, "track ids didn't match!")

    def test_track_listing(self):
        if DEBUG: print "----- this is TrackModelTests.test_track_listing"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        #print "--- type(instance): " + str(type(instance)) #<class 'c3sar.models.License'>
        #print "--- dir(instance): " + str(dir(instance)) # ... '_sa_instance_state', 'author',
                       # 'get_by_license_id', 'id', 'license_listing', 'metadata', 'name', 'url'
        #print "--- instance.id: " + str(instance.id) # 1
        from c3sar.models import Track
        result = Track.track_listing(order_by="NotImplemented")
        #print "--- result: " + str(result) # [<c3sar.models.License object at 0x9fba10c>]
        #print "--- dir(result): " + str(dir(result)) #
        #print "--- test_track_listing: result.__len__(): " + str(result.__len__()) # 1
        self.assertEqual(result.__len__(), 1, "we expect the result list to have one entry")


class UserModelTests(unittest.TestCase):
    if DEBUG: print "----- this is class UserModelTests "
    def setUp(self):
        self.session = _initTestingDB()
        self.session.close()
#        print "setUp(): type(self.session): " + str(type(self.session))
#        print "setUp(): dir(self.session): " + str(dir(self.session))

    def tearDown(self):
        #print dir(self.session)
        self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import User
        return User

    def _makeOne(self,
                 username=u'SomeUsername',
                 password=u'password',
                 surname=u'SomeSurname',
                 lastname=u'SomeLastname',
                 email=u'example@example.com',
                 email_is_confirmed=False,
                 email_confirmation_code=u'SomeTestCode'
                 ):
        return self._getTargetClass()(username,password,surname,lastname,
                                      email,email_is_confirmed,email_confirmation_code)


    def test_constructor(self):
        if DEBUG: print "----- this is UserModelTests.test_constructor "
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        self.assertNotEqual(instance.id, None, "did not get an id!")
        self.assertNotEqual(instance.id, '', "did not get an id!")
        self.assertEqual(instance.username, 'SomeUsername', "Not a match! Got a wrong value from the constructor.")
        self.assertEqual(instance.surname, 'SomeSurname', "Not a match!")
        self.assertEqual(instance.lastname, 'SomeLastname', "Not a match!")
        #print "UserModelTests.test_constructor: instance.password:" + instance.password
        # returns a hash:
        self.assertNotEqual(instance.password, 'password', "password was revealed (instead of hash)")
        # password does not reveal real password
        self.assertNotEqual(instance._get_password(), 'password', "Password was revealed")
        # password hash is not empty
        self.assertNotEqual(instance._get_password(), '', "Password hash was empty!")

    def test_user_listing(self):
        if DEBUG: print "----- this is UserModelTests.test_user_listing"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        user_cls = self._getTargetClass()
        result = user_cls.user_listing(order_by=None)
        #print "user_cls.user_listing('foo')" + repr(result)
        #print "UserModelTests.test_user_listing: result.__len__(): " + str(result.__len__())
        self.assertEqual(result.__len__(), 1, "Should have gotten 1 as result")


    def test_get_by_username(self):
        if DEBUG: print "----- this is UserModelTests.test_get_by_username"
        instance = self._makeOne()
        self.session.add(instance)
        #from c3sar.models import User
        myUserClass = self._getTargetClass()
        #print "myUserClass: " +str(myUserClass)
        #        print "str(myUserClass.get_by_username('SomeUsername')): " + str(myUserClass.get_by_username('SomeUsername'))
        foo = myUserClass.get_by_username(instance.username)
        #print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(instance.username, foo.username)
        self.assertEqual('SomeUsername', foo.username)


    def test_get_by_user_id(self):
        if DEBUG: print "----- this is UserModelTests.test_get_by_user_id"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        from c3sar.models import User
        result = User.get_by_user_id(1)
        self.assertEqual(instance.username, 'SomeUsername')
        self.assertEqual(result.username, 'SomeUsername')

    def test_check_password(self):
        if DEBUG: print "----- this is UserModelTests.test_check_password"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        result = self._getTargetClass().check_password(u'SomeUsername', u'password')
        #print "UserModelTests.test_check_password: result: " + str(result)
        self.assertTrue(result, "result was not True")

    def test_check_password_False(self):
        if DEBUG: print "----- this is UserModelTests.test_check_password_False"
        result = self._getTargetClass().check_password(u'nonexistant', u'somepassword')
        self.assertFalse(result, "result was not False")

    def test_check_username_exists(self):
        if DEBUG: print "----- this is UserModelTests.test_check_username_exists"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        from c3sar.models import User
        # this one does not extst
        result = User.check_username_exists(u'SomeUsernameNot')
        #print "UserModelTests.test_check_username_exists: result:" + str(result)
        #print "UserModelTests.test_check_username_exists: type(result):" + str(type(result))
        self.assertFalse(result, "result was not False")
        # this one must exist, return True
        result = User.check_username_exists(u'SomeUsername')
        #print "UserModelTests.test_check_username_exists: result:" + str(result)
        #print "UserModelTests.test_check_username_exists: type(result):" + str(type(result))
        self.assertTrue(result, "result was not True")

    def test_check_username_exists_False(self):
        """
        testing function 'check_username_exists' in models.User
        querying for a nonexistant user should return False
        """
        if DEBUG: print "----- this is UserModelTests.test_check_username_exists_False"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        result = self._getTargetClass().check_username_exists(u'nonexistant')
        self.assertEqual(result, False, "result was not False")

    def test_check_user_or_None(self):
        if DEBUG: print "----- this is UserModelTests.test_check_user_or_None"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        result = self._getTargetClass().check_user_or_None(u'SomeUsername')
        #print "UserModelTests.test_check_user_or_None: result:" + str(result)
        #print "UserModelTests.test_check_user_or_None: type(result):" + str(type(result))
        self.assertTrue(result, "result was not True")

    def test_check_user_or_None_None(self):
        if DEBUG: print "----- this is UserModelTests.test_check_user_or_None_None"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        result = self._getTargetClass().check_user_or_None(u'nonexistant')
        #print "result of check_user_or_None('nonexistant'): " +  str(result)
        self.assertEquals(result, None, "result was not None")


# class EmailAddressModelTests(unittest.TestCase):
#     if DEBUG: print "----- this is class EmailAddressModelTests "
#     def setUp(self):
#         self.session = _initTestingDB()

#     def tearDown(self):
#         #print dir(self.session)
#         #self.session.remove()
#         pass

#     def _getTargetClass(self):
#         from c3sar.models import EmailAddress
#         return EmailAddress

#     def _makeOne(self,
#                  email_address=u'test@shri.de'):
#         return self._getTargetClass()(email_address)


#     def test_constructor(self):
#         if DEBUG: print "----- this is EmailAddressModelTests.test_constructor"
#         instance = self._makeOne()
#         self.assertEqual(instance.email_address, 'test@shri.de')
#         self.assertEqual(instance.__repr__(), "<Address('test@shri.de')>")
#         #print "repr: " + instance.__repr__()


# class PhoneNumberModelTests(unittest.TestCase):
#     if DEBUG: print "----- this is class PhoneNumberModelTests "
#     def setUp(self):
#         self.session = _initTestingDB()

#     def tearDown(self):
#         #print dir(self.session)
#         #self.session.remove()
#         pass

#     def _getTargetClass(self):
#         from c3sar.models import PhoneNumber
#         return PhoneNumber

#     def _makeOne(self,
#                  phone_number='06421-98300422'):
#         return self._getTargetClass()(phone_number)


#     def test_constructor(self):
#         if DEBUG: print "----- this is PhoneNumberModelTests.test_constructor "
#         instance = self._makeOne()
#         self.assertEqual(instance.phone_number, '06421-98300422', "Got unecpected value from constructor!")
#         self.assertEqual(instance.__repr__(), "<PhoneNumber('06421-98300422')>", "Got unecpected value from constructor!")
#         #print "repr: " + instance.__repr__()

class BandModelTests(unittest.TestCase):
    if DEBUG: print "----- this is class BandModelTests "
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        #print dir(self.session)
        #self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import Band
        return Band

    def _makeOne(self,
                 name=u'Some Band',
                 email=u'someband@shri.de',
                 homepage=u'http://someband.net',
                 registrar=u'Some Registrar',
                 registrar_id=1):
        return self._getTargetClass()(name,email,homepage,registrar,registrar_id)


    def test_constructor(self):
        if DEBUG: print "----- this is BandModelTests.test_constructor "
        instance = self._makeOne()
        self.assertEqual(instance.name, 'Some Band', "Got unecpected value from constructor!")
        self.assertEqual(instance.email, 'someband@shri.de', "Got unecpected value from constructor!")
        self.assertEqual(instance.homepage, 'http://someband.net', "Got unecpected value from constructor!")
        self.assertEqual(instance.registrar, 'Some Registrar', "Got unecpected value from constructor!")
        #self.assertEqual(instance.__repr__(), "<Band('06421-98300422')>", "Got unecpected value from constructor!")
        #print "repr: " + instance.__repr__()

    def test_get_by_band_name(self):
        if DEBUG: print "----- this is BandModelTests.test_get_by_bandname"
        instance = self._makeOne()
        self.session.add(instance)
        myBandClass = self._getTargetClass()
        fooBand = myBandClass.get_by_band_name(instance.name)
        self.assertEqual(instance.name, fooBand.name)
        self.assertEqual('Some Band', fooBand.name)


    def test_get_by_band_id(self):
        if DEBUG: print "----- this is BandModelTests.test_get_by_band_id"
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        from c3sar.models import Band
        result = Band.get_by_band_id(1)
        self.assertEqual(instance.name, 'Some Band')
        self.assertEqual(result.name, 'Some Band')


    def test_band_listing(self):
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush() # to get the id from the db
        from c3sar.models import Band
        result = Band.band_listing(order_by=None)
        #print "--- result: " + str(result) # [<c3sar.models.License object at 0x9fba10c>]
        #print "--- dir(result): " + str(dir(result)) #
        #print "--- license_listing: result.__len__(): " + str(result.__len__()) # 1
        self.assertEqual(result.__len__(), 1, "we expect the result list to have one entry")

    def test_get_by_registrar_name(self):
        if DEBUG: print "----- this is BandModelTests.test_get_by_bandname"
        instance = self._makeOne()
        self.session.add(instance)
        myBandClass = self._getTargetClass()
        fooBandList = myBandClass.get_by_registrar_name(instance.registrar)
        if DEBUG:
            print "BandModelTests.test_get_by_registrar_name: fooBandList: " + str(fooBandList)
        #self.assertEqual(instance.registrar, fooBand.registrar)
        bandnames = []
        for band in fooBandList:
            bandnames.append(band.name)
        self.assertTrue('Some Band' in bandnames, "No Band found")



class TestPlaylistModel(unittest.TestCase):
    if DEBUG: print "----- this is class PlaylistModelTests "
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        #print dir(self.session)
        #self.session.remove()
        pass

    def _getTargetClass(self):
        from c3sar.models import Playlist
        return Playlist

    def _makeOne(self,
                 name=u'Some Playlist Name'):
        return self._getTargetClass()(name)


    def test_constructor(self):
        if DEBUG: print "----- this is BandModelTests.test_constructor "
        instance = self._makeOne()
        self.assertEqual(instance.name, 'Some Playlist Name', "Got unecpected value from constructor!")

    


## ideas for testing 'main', or at least having it covered:
# http://groups.google.com/group/pylons-devel/browse_thread/thread/e12a4dd55917c079


#class TestACLs(unittest.TestCase):
        #     # def test_acl(self):
        #     #     instance = self._makeOne()
        #     #     print "ACLs: " + repr(instance.__acl__())
        # # XXX ToDo: how to test the models ACLs?
        # # http://markmail.org/message/a2xii23tgktw67py has an answer

        #     def off_test_ACLs(self):
        #         import webtest
        #         from pyramid.exceptions import Forbidden
        #         from c3sar import main

        #         app = webtest.TestApp(main({}, **{'sqlalchemy.url': 'sqlite://'}))

        #         url = '/user/edit/2'
        #         # Make sure the view is not visible to the public
        #         self.assertRaises(Forbidden, app.get, url)
