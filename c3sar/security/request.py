### Making A 'User Object' Available as a Request Attribute
# https://docs.pylonsproject.org/projects/pyramid_cookbook/dev/authentication.html
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid
from c3sar.models import (
    User,
    #DBSession,
    )

class RequestWithUserAttribute(Request):
    @reify
    def user(self):
        #dbsession = DBSession()
        userid = unauthenticated_userid(self)
        print "--- in RequestWithUserAttribute: userid = " + userid
        if userid is not None:
            # this should return None if the user doesn't exist
            # in the database
            #return dbsession.query('users').filter(user.user_id == userid)
            return User.check_user_or_None(userid)
        return userid

# /end of ### Making A 'User Object' Available as a Request Attribute
