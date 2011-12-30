from c3sar.models import (
    User,
    Track,
    )
from pyramid.security import (
    Allow,
    Deny,
    )
from pyramid.security import ALL_PERMISSIONS


def groupfinder(userid, request):
    #print "=== this is the groupfinder ==="
    #user = User.get_by_user_id(userid)
    user = request.user
    if user:
        #print str(user.username)
        #print str(['%s' % g for g in user.groups])
        return ['%s' % g for g in user.groups]
#    if not user:
#        print "=== not user!"


### MAP GROUPS TO PERMISSIONS
class Root(object):
    __acl__ = [
        (Allow, 'system.Everyone', 'registerUser'),
        # (Allow, 'system.Authenticated', 'create'),
        # (Allow, 'g:editor', 'edit'),
        (Allow, 'group:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


class UserFactory(object):
    __acl__ = [
        (Allow, 'system.Everyone', 'registerUser'),
        (Allow, 'group:admins', 'editUser'),
        # (Allow, request.user.username, 'editUser'),  # WANTED !!!
        (Allow, 'group:accountants', 'activateUser'),
        ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        user = User.get_by_user_id(key)
        user.__parent__ = self
        user.__name__ = key
        return user


class TrackFactory(object):
    __acl__ = [
        (Allow, 'system.Everyone', 'viewTrack'),
#        (Deny, 'system.Everyone', 'edit'),
        #(Deny, '%s' % (request.user), 'edit'),
        (Allow, 'system.Authenticated', 'addTrack'),
        (Allow, 'group:admins', ('addTrack', 'editTrack')),
        ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        track = Track.get_by_track_id(key)
        track.__parent__ = self
        track.__name__ = key
        return track
