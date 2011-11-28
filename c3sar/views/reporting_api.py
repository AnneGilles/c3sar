from pyramid.request import Request
from pyramid.response import Response

from c3sar.models import (
    DBSession,
    # Report,
    )


#@view_config(route_name='api_report_single_airplay',
#             request_method ='GET')
def reporting_single_airplays_view(request):
    """
    this view is able to receive reporting data
    via rest api call
    """
    from_matchdict = request.matchdict['the_report']
    the_report = from_matchdict.encode('base64')

    #    dbsession = DBSession
    print "------------- got a new report! -----------------"
    print "base64 encoded: " + str(the_report)
    print "base64 decoded: " + str(the_report.decode('base64'))

    return Response("Thanks! got: %s" % the_report.decode('base64'))
