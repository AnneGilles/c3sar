import unittest
import os

DEBUG = True


class TestInitializeSql(unittest.TestCase):
    if DEBUG: print "----- this is class TestInitializeSql "

    def setUp(self):
        if DEBUG: print "----- this is class TestInitializeSql.setUp()"
        from sqlalchemy import create_engine
        from c3sar.models import DBSession
        from c3sar.models import Base
        from sqlalchemy.exc import IntegrityError

        # remove old database
        if os.path.isfile('testInitSql.db'):
            os.unlink('testInitSql.db')
            print "-- TestInitializeSql.setUp(): deleted testInitSql.db"
        self.engine = create_engine('sqlite:///testInitSql.db')
        #self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        #self.dbsession = DBSession()
        #return self.dbsession
        self.dbsession = DBSession

    def tearDown(self):
        if DEBUG: print "----- this is class TestInitializeSql.tearDown() "
        #from c3sar.models import DBSession
        #self.dbsession.remove()


    def _callFUT(self, engine):
        if DEBUG: print "----- this is class TestInitializeSql._callFUT() "
        from c3sar.models import initialize_sql
        return initialize_sql(engine)

    def test_initialize_sql(self):
        if DEBUG: print "----- this is class TestInitializeSql.test_initialize_sql() "
        self._callFUT(self.engine)
        from c3sar.models import User
        #print "--- DBSession.query(User).first().username: " + DBSession.query(User).first().username
        #print "--- DBSession.query(User).all(): "
        #rs = DBSession.query(User).all()
        #for item in rs:
        #    print item, item.username
        self.assertEqual(
            self.dbsession.query(User).first().username, 'firstUsername', "No match!")
