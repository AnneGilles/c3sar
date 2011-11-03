import formencode

from pyramid.view import view_config

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from c3sar.models import Band
from c3sar.models import User
from c3sar.models import DBSession

dbsession = DBSession()

# formencode schema for Bands ################################################

class BandSchema(formencode.Schema):
    allow_extra_fields = True  # needed for registrar_is_member checkbox,
    # see ../templates/band_add.pt
    #
    #filter_extra_fields = False
    band_name = formencode.validators.String(not_empty = True)
    band_homepage = formencode.validators.String(not_empty = False)
    band_email = formencode.validators.Email(not_empty = True,
                                             resolve_domain = False)
    

##################################################################### band_add
@view_config(route_name='band_add',
             permission='addBand',
             renderer='../templates/band_add.pt')
def band_add(request):
    
    form = Form(request, BandSchema)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash(form.data['band_name'])
        request.session.flash(form.data['band_homepage'])
        request.session.flash(form.data['band_email'])
        

    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')
        dbsession = DBSession()
        
#        band_registrar = authenticated_userid(request)
        band_registrar = request.user
        # request.session.flash("band_registrar: " + str(band_registrar)) # yields username
        #registrar = User.get_by_username(band_registrar)
        # request.session.flash("registrar: " + str(registrar)) # yields object
        #request.session.flash("registrar.user_id: " + str(registrar.user_id))

        
        request.session.flash("reg_is_member: " + form.data['registrar_is_member'])
        is_member = form.data['registrar_is_member']

        #if is_member == 1:
 
        band = Band(
            name = form.data['band_name'],
            homepage = form.data['band_homepage'],
            email = form.data['band_email'],
            registrar = request.user.username,
            registrar_id = request.user.id,
            )

        dbsession.add(band)
        request.session.flash(u'writing to database ...')

        # request.session.flash('id' + str(band.band_id)) # is None

        dbsession.flush()

        redirect_url = "/band/view/" + str(band.id)

        request.session.flash( redirect_url)

        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location = redirect_url)

    return {
        'viewer_username': authenticated_userid(request),
        'form': FormRenderer(form)
        }

##################################################################### band_edit
@view_config(route_name='band_edit',
             permission='view',
             renderer='../templates/band_edit.pt')
def band_edit(request):
    
    band_id = request.matchdict['band_id']
    band = Band.get_by_band_id(band_id)

    # no change through form, so reuse old value (for now)
    band_registrar = band.band_registrar
    band_registrar_id = band.band_registrar_id

    form = Form(request, BandSchema, obj = band)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash(form.data['band_name'])
        request.session.flash(form.data['band_homepage'])
        request.session.flash(form.data['band_email'])
        

    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')
        dbsession = DBSession()
 
        band = Band(
            band_name = form.data['band_name'],
            band_homepage = form.data['band_homepage'],
            band_email = form.data['band_email'],
            band_registrar = band_registrar,
            band_registrar_id = band_registrar_id
            )

        dbsession.add(band)
        request.session.flash(u'writing to database ...')

        dbsession.flush()
        # ToDo: https://redmine.local/issues/5

    return {
        'viewer_username': authenticated_userid(request),
        'form': FormRenderer(form)
        }

#################################################################### band_view
from pyramid.security import authenticated_userid

@view_config(route_name='band_view',
             permission='view',
             renderer='../templates/band_view.pt')
def band_view(request):

    band_id = request.matchdict['band_id']
    band = Band.get_by_band_id(band_id)

    #calculate for next/previous-navigation    
    if int(band_id) == 1:
        prev_id = 1
    else:
        prev_id = int(band_id) - 1
    
    next_id = int(band_id) + 1
    # TODO: MAXiD
    # if band_id == MaxId: next_id = band_id
    

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)



    return {
        'band': band,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id
        }

#################################################################### band_list
@view_config(route_name='band_list',
             permission='view',
             renderer='../templates/band_list.pt')
def band_list(request):
    #dbsession = DBSession()
    bands = Band.band_listing(Band.id.desc())
    return {'bands': bands}
