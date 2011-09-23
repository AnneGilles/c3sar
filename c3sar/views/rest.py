
from pyramid.view import view_config
from pyramid.request import Request
from pyramid.response import Response

@view_config(route_name = 'api_get_user',
             request_method = 'GET')
def show_user_view(request):
    return Response("GET user %s" % request.matchdict['id'])

@view_config(route_name = 'post',
             request_method = 'DELETE')
def delete_user_view(request):
    # delete that user
    return Response("DELETE user %s" % request.matchdict['id'])


# # # http://zhuoqiang.me/a/restful-pyramid
 # # # http://stackoverflow.com/questions/5459736/python-restful-webservice-framework-roll-my-own-or-is-there-a-recommended-librar


# # # http://code.creativecommons.org/viewsvn/api_client/trunk/python/
