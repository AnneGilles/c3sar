# this suite of tests was inspired by pyramid 1.2 documentation (PDF)

import unittest
from pyramid import testing

DEBUG = False

def _initTestingDB():
    from c3sar.models import DBSession
    from c3sar.models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

def _registerRoutes(config):
    config.add_route('home', '/')

class InitializeSqlTests(unittest.TestCase):

    def setUp(self):
        from c3sar.models import DBSession
        DBSession.remove()
    
    def tearDown(self):
        from c3sar.models import DBSession
        DBSession.remove()
        #    self.session.remove()
            
    def _callFUT(self, engine):
        from c3sar.models import initialize_sql
        return initialize_sql(engine)

    def test_it(self):
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        self._callFUT(engine)
        from c3sar.models import DBSession, User

        if DEBUG:
            print str(DBSession.query(User).first())
            print str(DBSession.query(User).first().username)

        self.assertEqual(DBSession.query(User).first().username,
                         'firstUsername')
