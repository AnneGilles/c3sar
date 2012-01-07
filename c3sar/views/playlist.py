import formencode
import colander
from colander import (
    Range,
    datetime,
    )
import deform
from deform import ValidationFailure

from translationstring import TranslationStringFactory

from pyramid.url import route_url
from pyramid.i18n import (
    get_locale_name,
    get_localizer,
    )

from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from wtforms import (
    Form,
    TextField,
    validators,
    )

from c3sar.models import (
    Playlist,
    DBSession,
    )

_ = TranslationStringFactory('c3sar')

dbsession = DBSession()

#DEBUG = True
DEBUG = False

if DEBUG:  # pragma: no cover
    import pprint
    pp = pprint.PrettyPrinter(indent=4)


def playlist_list(request):
    """list all playlists"""
    playlists = Playlist.playlist_listing(Playlist.id.desc())
    return {
        'playlists': playlists
        }


class PlaylistCreationForm(Form):
    name = TextField('Playlist Name', [validators.Length(min=1, max=30)])


def playlist_add(request):
    """add a playlist (of tracks)"""
    #print "this is playlist_add"
    #print request.method
    #print request.POST
    form = PlaylistCreationForm(request.POST)
    
    if request.method == 'POST' and form.validate():

        dbsession = DBSession()

        pl = Playlist(
            name=form.name.data,
            issuer=authenticated_userid(request))
        #print pl
        #print pl.name
        dbsession.add(pl)
        dbsession.flush()
        #print pl.id
        return HTTPFound(
            route_url('playlist_view', request, playlist_id=pl.id))

    return {'form': form}


def playlist_view(request):
    id = request.matchdict['playlist_id']
    #print "id: " + str(id)
    playlist = Playlist.get_by_id(id)

    if not isinstance(playlist, Playlist):
        msg = "Playlist id not found in database"
        #print "Playlist id not found in database"
        return HTTPFound(request.route_url('not_found'))

    #calculate for next/previous-navigation
    max_id = Playlist.get_max_id()
    #previous
    if playlist.id == 1:           # if looking at first id
        prev_id = max_id       # --> choose highest id
    else:                      # if looking at other id
        prev_id = playlist.id - 1  # --> choose previous
    # next
    if playlist.id != max_id:      # if not on highest id
        next_id = playlist.id + 1  # --> choose next
    elif playlist.id == max_id:    # if highest_id
        next_id = 1            # --> choose first id ('wrap around')

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)

    return {
        'playlist': playlist,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id
        }

#class PlaylistEditSchema(formencode.Schema):
#    allow_extra_fields = True
#    name = formencode.validators.String(not_empty=True)


def playlist_edit(request):

    id = request.matchdict['playlist_id']
    #print "id: " + str(id)
    playlist = Playlist.get_by_id(id)
    #print "playlist: " + str(playlist)
    if not isinstance(playlist, Playlist):
        msg = "Playlist id not found in database"
        #print "Playlist id not found in database"
        return HTTPFound(request.route_url('not_found'))

    # no change through form, so reuse old value (for now)
    playlist_issuer = playlist.issuer

    locale_name = get_locale_name(request)
    #print locale_name

    appstruct = {
        u'name': playlist.name
        }

    class PlayDateSequence(colander.SequenceSchema):
        date = colander.SchemaNode(
            colander.Date(),
            title=_('Play Date'),
            validator=Range(
                min=datetime.date(2010, 1, 1),
                min_err=_('${val} is earlier than earliest date ${min}')
                )
            )

    class PlaylistSchema(colander.Schema):
        name = colander.SchemaNode(
            colander.String(),
            )
        dates = PlayDateSequence()
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=locale_name
            )

    schema = PlaylistSchema()
    form = deform.Form(schema,
                       buttons=[deform.Button('submit', _('Submit'))])

    #print "the request: "
    #    print request
    #pp.pprint(request.POST.items())

    if 'submit' in request.POST:
        # form was submitted
        print "form was submitted !!!"

        try:  # will it validate?
            appstruct = form.validate(request.POST.items())
            #pp.pprint(appstruct)
            return {
                'form': form.render(appstruct)  # , True)
                }

        # if it does not validate, show it again
        except ValidationFailure, e:
            return {'form': e.render()}

# and not form.validate():
        #         # form didn't validate
#         request.session.flash('form does not validate!')
#         request.session.flash(form.data['name'])
#         #request.session.flash(form.data['homepage'])
#         #request.session.flash(form.data['email'])

# #    print form.validate(appstruct)

#     if 'form.submitted' in request.POST and form.validate():

#         if form.data['name'] != playlist.name:
#             playlist.name = form.data['name']
#             if DEBUG:  # pragma: no cover
#                 print "changing playlist name"
#                 request.session.flash('changing playlist name')

#         request.session.flash(u'writing to database ...')
#         dbsession.flush()
#         # if all went well, redirect to band view
#         return HTTPFound(
#             route_url('playlist_view', request, playlist_id=playlist.id))

    # default: if page is opened: render available data
    return {
        'viewer_username': authenticated_userid(request),
        'form': form.render(appstruct)
        }
