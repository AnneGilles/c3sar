from sqlalchemy.exc import ProgrammingError

from pyramid.httpexceptions import HTTPNotFound

from pyramid.view import view_config
#from pyramid.url import route_url
from pyramid.url import resource_url
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound

from pyramid.security import (
    authenticated_userid,
    remember,
    forget,
    )

from c3sar.models import (
    User,
    DBSession,
    Band,
    Track,
    Playlist
    )

dbsession = DBSession()


# ###################################################### home_view
@view_config(permission='view',
             route_name='home',
             renderer='../templates/main.pt')
def home_view(request):
    try:
        num_users = dbsession.query(User).count()
        num_tracks = dbsession.query(Track).count()
        # num_tracks = 0
        num_bands = dbsession.query(Band).count()
        # num_bands = 0
    except ProgrammingError, pe:
        # ProgrammingError: (ProgrammingError)
        # SQLite objects created in a thread can only be used in that same
        # thread.The object was created in thread id -1333776384
        # and this is thread id -1329573888
        print "not a bug, a feature: logout first, please!"
        return HTTPFound(route_url('logout', request))

    logged_in = authenticated_userid(request)
    user_id = User.get_by_username(logged_in)

    return dict(
        logged_in=logged_in,
        num_users=num_users,
        num_tracks=num_tracks,
        num_bands=num_bands,
        user_id=user_id
        )


# ######################################################### listen

@view_config(route_name='listen',
             renderer='../templates/listen.pt',
             permission='view')
def listen_view(request):

    request.session.pop_flash()
#    dbsession = DBSession()
#    tracks = dbsession.query(Track).join('')
#    request.session.flash('tracks: ' + str(tracks))
#    request.session.flash(dir(tracks))

#    tracks = Track.tracks_bunch(Track.track_id.desc())

    return {  # 'tracks': tracks,
            'foo': 'bar',
            }


# ######################################################### about
@view_config(route_name='about',
             permission='view',
             renderer='../templates/about.pt')
def about_view(request):
#    return {'foo', 'bar'}
    return dict(
        logged_in=authenticated_userid(request)
        )


# ######################################################### 404
# http://docs.pylonsproject.org/projects/pyramid/1.1/narr/hooks.html
#                                        #changing-the-notfound-view
def notfound_view(context, request):
    return HTTPNotFound('It aint there, stop trying!')


# http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/static.html
#                                    #serving-a-single-file-from-the-root
from pyramid.response import Response
import os

_here = os.path.dirname(__file__)
_parent = os.path.join(_here, '..')
_icon = open(os.path.join(
        _parent, 'static', 'favicon.ico')).read()
_fi_response = Response(content_type='image/x-icon',
                        body=_icon)


@view_config(name='favicon.ico')
def favicon_view(request):
    return _fi_response


@view_config(route_name='not_implemented',
             permission='view',
             renderer='../templates/not_implemented.pt')
def not_implemented_view(request):
    return dict(
        msg='not implemented'
        )


@view_config(route_name='not_found',
             permission='view',
             renderer='../templates/not_found.pt')
def not_found_view(request):
    return dict(
        msg='not found'
        )


def not_allowed_view(request):
    #import pdb
    #pdb.set_trace()
    request.response_status = 403
#    request.response_headerlist = [
#        ('Location', 'http://localhost/track/view/3'),
#        ('Content-Type', 'text/plain; charset=UTF-8'),
#        ('Content-Length', '109')]
    return dict(
#        message='no message'
        )
