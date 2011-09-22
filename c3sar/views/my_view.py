from c3sar.models import DBSession
#from c3sar.models import MyModel

def my_view(request):
    dbsession = DBSession()
    #root = dbsession.query(MyModel).filter(MyModel.name==u'root').first()
    return {'root':'foo', 'project':'c3sar'}
