# -*- coding: utf-8 -*-
import transaction
from datetime import datetime
import cryptacular.bcrypt

# sqlalchemy stuff
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
)

from sqlalchemy.types import (
    Integer,
    Unicode,
    Boolean,
    DateTime,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    synonym,
)
from sqlalchemy.sql import func

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Allow

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

# s3 stuff
#from c3sar.s3 import (
#    initialize_s3,
#    I2S3,
#)

# password crypt
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def hash_password(password):
    return unicode(crypt.encode(password))


class User(Base):
    """
    applications user model
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), unique=True)
    surname = Column(Unicode(255))
    lastname = Column(Unicode(255))

    # address
    street = Column(Unicode(255))
    number = Column(Unicode(255))
    postcode = Column(Unicode(255))
    city = Column(Unicode(255))
    country = Column(Unicode(255))

    # contact
    fax = Column(Unicode(255))
    phone = Column(Unicode(255))
    email = Column(Unicode(255))
    email_is_confirmed = Column(Boolean, default=False)
    email_confirm_code = Column(Unicode(255))

    # account meta
    date_registered = Column(DateTime(), nullable=False)
    last_login = Column(DateTime(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_password_change = Column(DateTime,
                                  default=func.current_timestamp())
    _password = Column('password', Unicode(60))

    # groups = relationship(Group,
    #                       secondary=users_groups,
    #                       backref="users")

    @property
    def __acl__(self):
        return [
            (Allow,                           # user may edit herself
             'user:%s' % self.id, 'editUser'),
            (Allow,                           # accountant group may edit
             'group:accountant', ('view', 'editUser')),
            (Allow,                           # admin group may edit
             'group:admin', ('view', 'editUser')),
            ]

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

#    def get_group_list(self):
#        return [ str(group.name) for group in self.groups ]

    def __init__(self, username, password, surname, lastname,
                 email, email_is_confirmed, email_confirm_code,
                 phone, fax):
        self.username = username
        self.surname = surname
        self.lastname = lastname
        self.password = password
        self.email = email
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.phone = phone
        self.fax = fax
        self.date_registered = datetime.now()
        self.last_login = datetime.now()

    def set_address(self, street, number, postcode, city, country):
        self.street = street
        self.number = number
        self.postcode = postcode
        self.city = city
        self.country = country

    @classmethod
    def get_by_username(cls, username):
        dbSession = DBSession()
        return dbSession.query(cls).filter(cls.username == username).first()

    @classmethod
    def get_by_user_id(cls, id):
        dbSession = DBSession()
        return DBSession.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_max_id(cls):
        """return the highest id (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def check_password(cls, username, password):
        dbSession = DBSession()
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)

    @classmethod
    def check_username_exists(cls, username):
        """
        check whether a user by that username exists in the database.
        if yes, we cannot have a user register with that name.

        returns True if username is taken
        """
        user = cls.get_by_username(username)
        if user:
            return True
        return False

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, username):
        """
        check whether a user by that username exists in the database.
        if yes, return that object, else None.

        returns None if username doesn't exist
        """
        user = cls.get_by_username(username)
        if not user:
            return None
        return user

    @classmethod
    def user_listing(cls, order_by, how_many=10):
        q = DBSession.query(cls).all()
        # return q.order_by(order_by)[:how_many]
        return q


class License(Base):
    """
    A license attributed to a work.
    There is an infinite number of possible licenses,
    so we better store them.
    """
    __tablename__ = 'licenses'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    uri = Column(Unicode(255))
    img = Column(Unicode(255))
    author = Column(Unicode(255))

    def __init__(self,
                 name,
                 uri,
                 img,
                 author,
                 ):
        self.name = name
        self.uri = uri
        self.img = img
        self.author = author

    @classmethod
    def get_by_license_id(cls, license_id):
        return DBSession.query(cls).filter(cls.id == license_id).first()

    @classmethod
    def get_max_id(cls):
        """return the highest id (by counting rows in table)"""
        return DBSession.query(cls).count()

#    def license_listing(cls, order_by, how_many=10):
    @classmethod
    def license_listing(cls, how_many=10):
        q = DBSession.query(cls).all()
#        return q.order_by(order_by)[:how_many]
        return q


# table for relation between bands and members(=users)
bands_members = Table('bands_members', Base.metadata,
    Column('band_id', Integer, ForeignKey('bands.id'),
        primary_key=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'),
        primary_key=True, nullable=False))

# table for relation between bands and their tracks
bands_tracks = Table('bands_tracks', Base.metadata,
    Column('band_id', Integer, ForeignKey('bands.id'),
        primary_key=True, nullable=False),
    Column('tracks_id', Integer, ForeignKey('tracks.id'),
        primary_key=True, nullable=False))

# relation between licenses and tracks
licenses_tracks = Table('licenses_tracks', Base.metadata,
    Column('license_id', Integer, ForeignKey('licenses.id')),
    Column('track_id', Integer, ForeignKey('tracks.id')))

track_license = Table('track_license',
                      Base.metadata,
                      Column('track_id', Integer, ForeignKey('tracks.id')),
                      Column('license_id', Integer, ForeignKey('licenses.id'))
                      )


class Track(Base):  # #########################################################
    """
    A Track. some music -- or just some metadata!
    """
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    url = Column(Unicode(255))
    album = Column(Unicode(255))
    filepath = Column(Unicode(255))
    bytesize = Column(Integer)

    license = relationship("License",
                           secondary='track_license',
                           #primaryjoin="_and(Track.id==License.track_id)",
                           order_by="License.id")
    # track_composers = reference to User(s) or 'some text'
    # track_lyrics = reference to User(s) or 'some text'

    def __init__(self, name, album, url, filepath, bytesize):
        self.name = name
        self.album = album
        self.url = url
        self.filepath = filepath
        self.bytesize = bytesize
#        self.license = license

    @classmethod
    def get_by_track_name(cls, track_name):
        return DBSession.query(cls).filter(cls.name == track_name).first()

    @classmethod
    def get_by_track_id(cls, track_id):
        return DBSession.query(cls).filter(cls.id == track_id).first()

    @classmethod
    def get_max_id(cls):
        """return the highest id (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def track_listing(cls, order_by, how_many=10):
        q = DBSession.query(cls).all()
        return q

    # ToDo Album listing


class Band(Base):  # ################################################## B A N D
    """
    A Band
    consists of Artists
    has Tracks
    gets a Bucket --> ToDo
    gets money in the long run
    """
    __tablename__ = 'bands'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    homepage = Column(Unicode(255))
    email = Column(Unicode(100))
    registrar_id = Column(Integer,
                          ForeignKey('users.id'))  # who registered this band?
    registrar = Column(Unicode(255))
    date_registered = Column(DateTime(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    members = relationship(User,
                           secondary=bands_members,
                           backref="bands")
    tracks = relationship(Track,
                           secondary=bands_tracks,
                           backref="bands")
    #band_registrar_rel = relation(User, cascade="delete", backref="bands")
    # band_tracks = list of tracks...
    # band_bucket ...
    # band_bank_account ...

    def __init__(self,
                 name,
                 email,
                 homepage,
                 registrar,
                 registrar_id):

        self.name = name
        self.email = email
        self.homepage = homepage
        self.registrar = registrar
        self.registrar_id = registrar_id
        self.date_registered = datetime.now()

    @classmethod
    def get_by_band_name(cls, band_name):
        return DBSession.query(cls).filter(cls.name == band_name).first()

    @classmethod
    def get_by_band_id(cls, band_id):
        return DBSession.query(cls).filter(cls.id == band_id).first()

    @classmethod
    def get_max_id(cls):
        """return the highest id (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def band_listing(cls, order_by, how_many=10):
        q = DBSession.query(cls).all()
#        return q.order_by(order_by)[:how_many]
        return q

    @classmethod  # find all bands a person has registered
    def get_by_registrar_name(cls, registrar_name):
        """
        returns a list of bands
        """
        return DBSession.query(cls).filter(
            cls.registrar == registrar_name
            ).all()


class Playlist(Base):  # ####################################################
    """
    The Playlist definition. A Playlist is...

    a list of tracks, containing
     - the date they were played,
    """
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=False)
    issuer = Column(Integer, ForeignKey('users.id'))
    # list of track ids .... = Column(Integer)
    date_created = Column(DateTime,
                                  default=func.current_timestamp())

    def __init__(self, name, issuer):
        self.name = name
        self.issuer = issuer
        self.date_created = datetime.now()
        #self.value = value

    @classmethod
    def get_by_id(cls, id):
        dbSession = DBSession()
        return DBSession.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_max_id(cls):
        """return the highest id (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def playlist_listing(cls, order_by, how_many=10):
        q = DBSession.query(cls).all()
        return q


def populate():
    dbsession = DBSession()
    transaction.begin()  # this is needed to make the webtest tests not fail

    user1 = User(username=u'firstUsername', surname=u'firstSurname',
                 lastname=u'firstLastname', password=u'password',
                 email=u'first1@shri.de', email_confirm_code=u'barfbarf',
                 email_is_confirmed=True,
                 phone=u'+49 6421 968300422',
                 fax=u'+49 6421 690 6996',
                 )
    user1.set_address(street=u'Teststraße', number=u'1234a',
                      postcode=u'35039', city=u'Marburg Mitte',
                      country=u'Deutschland')
    dbsession.add(user1)

    user2 = User(username=u'secondUsername', surname=u'secondSurname',
                 lastname=u'secondSurname', password=u'password',
                 email=u'second1@shri.de', email_confirm_code=u'möökmöök',
                 email_is_confirmed=False,
                 phone=u'+49 6421 968300421',
                 fax=u"",
                 )
    dbsession.add(user2)

    band1 = Band(name=u"TestBand1", email=u"testband1@shri.de",
                 homepage=u"http://testband.io", registrar=u"hans",
                 registrar_id=1)
    dbsession.add(band1)

    band2 = Band(name=u"TestBand2", email=u"testband2@shri.de",
                 homepage=u"http://testband.com", registrar=u"paul",
                 registrar_id=2)
    dbsession.add(band2)

    # track1 = Track(name=u"TestTrack1", album=u'TestAlbum1',
    #                url=u'http://testband.io/t1.mp3', filepath=None,
    #                bytesize=None)
    # dbsession.add(track1)

    track2 = Track(name=u"TestTrack2", album=u'TestAlbum2',
                   url=u'http://testband.io/t2.mp3', filepath=None,
                   bytesize=None,
                   )
    track2.license = [
        License(
            name=u"Creative Commons Attribution 3.0 Unported",
            uri=u"http://creativecommons.org/licenses/by/3.0/",
            img=u"http://i.creativecommons.org/l/by/3.0/88x31.png",
            author=u"Somebody"
            )
        ]
    dbsession.add(track2)

    # <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">
    # <img alt="Creative Commons License" style="border-width:0"
    #     src="http://i.creativecommons.org/l/by/3.0/88x31.png" /></a><br />
    # This work is licensed under a <a rel="license"
    #     href="http://creativecommons.org/licenses/by/3.0/">
    #     Creative Commons Attribution 3.0 Unported License</a>.
    license1 = License(name=u"Creative Commons Attribution 3.0 Unported",
                       uri=u"http://creativecommons.org/licenses/by/3.0/",
                       img=u"http://i.creativecommons.org/l/by/3.0/88x31.png",
                       author=u"Somebody")
    dbsession.add(license1)

    license2 = License(name=u"All Rights reserved",
                       uri=u"",
                       img=u"",
                       author=u"Somebody")
    dbsession.add(license2)

    # add a playlist
    pl1 = Playlist(name=u'foo', issuer=user1.id)
    dbsession.add(pl1)

    try:
        dbsession.flush()
    except Exception, e:  # PRAGMA: no cover
        dbsession.rollback()
        print "--- ROLLBACK cause:  -------------------------------------- "
        print str(e)
        print "----------------------------------------------------------- "
    transaction.commit()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError, e:  # PRAGMA: no cover
        print "--- initialize_sql aborted due to IntegrityError: "
        print e
        transaction.abort()
