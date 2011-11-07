from types import NoneType

from pyramid.view import view_config
from pyramid.request import Request
from pyramid.response import Response

from c3sar.models import (
    DBSession,
    User,
    )

#@view_config(route_name = 'api_get_user',
#             request_method = 'GET')
def show_user_view(request):
    user = User.get_by_user_id(request.matchdict['id'])
    if isinstance(user, NoneType):
        return Response('null')
    return Response("%s : %s" % (user.id, user.username) )

@view_config(route_name = 'post',
             request_method = 'DELETE')
def delete_user_view(request):
    # delete that user
    return Response("DELETE user %s" % request.matchdict['id'])


# # # http://zhuoqiang.me/a/restful-pyramid
 # # # http://stackoverflow.com/questions/5459736/python-restful-webservice-framework-roll-my-own-or-is-there-a-recommended-librar


# # # http://code.creativecommons.org/viewsvn/api_client/trunk/python/
