import transaction
from datetime import datetime
import cryptacular.bcrypt

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    synonym,
)
from sqlalchemy.sql import func

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

def hash_password(password):
    return unicode(crypt.encode(password))

def a_random_string():
    import random, string
    N = 6   # length of string to be produced 
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))

class EmailAddress(Base):
    __tablename__ = 'email_addresses'
    id = Column((Integer), primary_key=True)
    email_address = Column(String, nullable = False)
    confirm_code = Column(Unicode(10))
    is_confirmed = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))

#    user = relationship("User", backref=backref('addresses', order_by=id))

    def __init__(self, email_address):
        self.email_address = email_address
        self.confirm_code = a_random_string()
        self.is_confirmed = False

    def __repr__(self):
        return "<Address('%s')>" % self.email_address

class PhoneNumber(Base):
    __tablename__ = 'phone_numbers'
    id = Column((Integer), primary_key=True)
    phone_number = Column(String, nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))

#    user = relationship("User", backref=backref('phone_numbers', order_by=id))

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def __repr__(self):
        return "<PhoneNumber('%s')>" % self.phone_number

class User(Base): # ===========================================================
    """
    applications user model
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), unique=True)
    surname = Column(Unicode(255))
    lastname = Column(Unicode(255))
    telefax = Column(Unicode(255))
    phone_numbers = relationship("PhoneNumber", order_by="PhoneNumber.id")
    email_addresses = relationship("EmailAddress", order_by="EmailAddress.id")
    date_registered = Column(DateTime(), nullable=False)
    last_login = Column(DateTime(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_password_change = Column(DateTime,
                                  default = func.current_timestamp())

    _password = Column('password', Unicode(60))

    # groups = relationship(Group,
    #                       secondary=users_groups,
    #                       backref="users")

    @property
    def __acl__(self):
        return [
            (Allow, 'user:%s' % self.id, 'editUser'), # user may edit herself
            (Allow, 'group:accountant', ('view', 'editUser')),  # accountant group may edit
            (Allow, 'group:admin', ('view', 'editUser')),  # admin group may edit
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
                 email, email_conf, email_conf_code,):
        self.username = username
        self.surname = surname
        self.lastname = lastname
        self.email = email
        self.email_conf = email_conf
        self.email_conf_code = email_conf_code
        self.password = password
        self.date_registered = datetime.now()
        self.last_login = datetime.now()

    @classmethod
    def get_by_username(cls, username):
        #from mortar_rdb import getSession
        dbSession = DBSession()
        return dbSession.query(cls).filter(cls.username==username).first()

    @classmethod
    def get_by_user_id(cls, id):
        dbSession = DBSession()
        return DBSession.query(cls).filter(cls.id==id).first()

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



class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

def populate():
    session = DBSession()
    model = MyModel(name=u'root', value=55)
    session.add(model)
    session.flush()
#    transaction.commit()

    user1 = User(username='eins', surname='sur eins', lastname='last eins',
                 email='eins@shri.de', email_conf=False, email_conf_code='QWERTZ',
                 password='password')
 
    user1.email_addresses = [ EmailAddress(email_address = 'test@shri.de',) ]
    session.add(user1)

    session.flush()
    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()
