import formencode

from pyramid.url import route_url
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from c3sar.models import (
    Band,
    User,
    DBSession,
    )

dbsession = DBSession()


# formencode schema for Bands ################################################
class BandSchema(formencode.Schema):
    allow_extra_fields = True  # needed for registrar_is_member checkbox,
    # see ../templates/band_add.pt
    #
    #filter_extra_fields = False
    band_name = formencode.validators.String(not_empty=True)
    band_homepage = formencode.validators.String(not_empty=False)
    band_email = formencode.validators.Email(not_empty=True,
                                             resolve_domain=False)


class BandEditSchema(formencode.Schema):
    allow_extra_fields = True  # needed for registrar_is_member checkbox,
    # see ../templates/band_add.pt
    #
    #filter_extra_fields = False
    name = formencode.validators.String(not_empty=True)
    homepage = formencode.validators.String(not_empty=False)
    email = formencode.validators.Email(not_empty=True,
                                        resolve_domain=False)


# #################################################################### band_add
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
        band_registrar = request.user
        request.session.flash(
            "reg_is_member: " + form.data['registrar_is_member'])
        is_member = form.data['registrar_is_member']
        #if is_member == 1:
        band = Band(
            name=form.data['band_name'],
            homepage=form.data['band_homepage'],
            email=form.data['band_email'],
            registrar=request.user.username,
            registrar_id=request.user.id,
            )

        dbsession.add(band)
        request.session.flash(u'writing to database ...')

        # request.session.flash('id' + str(band.band_id)) # is None

        dbsession.flush()

        redirect_url = "/band/view/" + str(band.id)

        request.session.flash(redirect_url)

        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location=redirect_url)

    return {
        'viewer_username': authenticated_userid(request),
        'form': FormRenderer(form)
        }


# ################################################################### band_edit
@view_config(route_name='band_edit',
             permission='view',
             renderer='../templates/band_edit.pt')
def band_edit(request):

    band_id = request.matchdict['band_id']
    band = Band.get_by_band_id(band_id)

    if not isinstance(band, Band):
        msg = "Band id not found in database"  # TODO: check template!
        return HTTPFound(route_url('not_found', request))

    # no change through form, so reuse old value (for now)
    band_registrar = band.registrar
    band_registrar_id = band.registrar_id

    form = Form(request, schema=BandEditSchema, obj=band)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        #request.session.flash(form.data['name'])
        #request.session.flash(form.data['homepage'])
        #request.session.flash(form.data['email'])

    if 'form.submitted' in request.POST and form.validate():
        #request.session.flash('form validated!')
        dbsession = DBSession()

        if form.data['name'] != band.name:
            band.name = form.data['name']
            #request.session.flash('changing band name')
        if form.data['homepage'] != band.homepage:
            band.homepage = form.data['homepage']
            #request.session.flash('changing band homepage')
        if form.data['email'] != band.email:
            band.email = form.data['email']
            #request.session.flash('changing band email')

        #request.session.flash(u'writing to database ...')
        dbsession.flush()

    return {
        'viewer_username': authenticated_userid(request),
        'form': FormRenderer(form)
        }


#################################################################### band_view
@view_config(route_name='band_view',
             permission='view',
             renderer='../templates/band_view.pt')
def band_view(request):

    band_id = request.matchdict['band_id']
    band = Band.get_by_band_id(band_id)

    # redirect if id does not exist in database
    if not isinstance(band, Band):
        request.session.flash('this id wasnt found in our database!')
        return HTTPFound(route_url('not_found', request))

    #calculate for next/previous-navigation
    max_id = Band.get_max_id()
    #previous
    if band.id == 1:           # if looking at first id
        prev_id = max_id       # --> choose highest id
    else:                      # if looking at other id
        prev_id = band.id - 1  # --> choose previous
    # next
    if band.id != max_id:      # if not on highest id
        next_id = band.id + 1  # --> choose next
    elif band.id == max_id:    # if highest_id
        next_id = 1            # --> choose first id ('wrap around')

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)

    return {
        'band': band,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id
        }


# ################################################################### band_list
@view_config(route_name='band_list',
             permission='view',
             renderer='../templates/band_list.pt')
def band_list(request):
    #dbsession = DBSession()
    bands = Band.band_listing(Band.id.desc())
    return {'bands': bands}
