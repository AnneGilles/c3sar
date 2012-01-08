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
            issuer=request.user.id
            )

        #print pl
        #print pl.name
        #print pl.issuer
        dbsession.add(pl)
        dbsession.flush()
        #print pl.id
        return HTTPFound(
            route_url('playlist_view', request, playlist_id=pl.id)
            )

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
    playlist = Playlist.get_by_id(id)
    if DEBUG:  # pragma: no cover
        print "playlist from matchdict for editing: " + str(playlist)

    if not isinstance(playlist, Playlist):
        # the playlist to be edited could not be found
        msg = "Playlist id not found in database"
        #print "Playlist id not found in database"
        return HTTPFound(request.route_url('not_found'))

    # issuer: no change through form, so reuse old value (for now)
    playlist_issuer = playlist.issuer

    locale_name = get_locale_name(request)
    if DEBUG:   # pragma: no cover
        print "locale name: " + locale_name

    appstruct = {               # load playlist name into appstruct
        u'name': playlist.name
        }

    class PlaylistEntrySchema(colander.Schema):
        '''this is how a playlist entry will look like in the form '''
        date = colander.SchemaNode(
            colander.Date(),
            title=_('Play Date'),
            validator=Range(
                min=datetime.date(2010, 1, 1),
                min_err=_('${val} is earlier than earliest date ${min}')
                )
            )
        track = colander.SchemaNode(
            colander.String(),
            title=_('Track Name')
            )
        artist = colander.SchemaNode(
            colander.String(),
            title=_('by Artist:')
            )
        length = colander.SchemaNode(
            colander.String(),
            title=_('Length')
            )

    class PlaylistEntrySequence(colander.SequenceSchema):
        '''a sequence/list of playlist entries '''
        entry = PlaylistEntrySchema()

    class PlaylistSchema(colander.Schema):
        '''a playlist has a name and a sequence of entries'''
        name = colander.SchemaNode(
            colander.String(),
            )
        entries = PlaylistEntrySequence()
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=locale_name
            )

    schema = PlaylistSchema()
    form = deform.Form(schema,
                       buttons=[deform.Button('submit', _('Submit'))])

    if 'submit' in request.POST:              # form was submitted
        if DEBUG:  # pragma: no cover
            print "form was submitted !!!"

        try:  # will it validate?
            appstruct = form.validate(request.POST.items())

            if DEBUG:  # pragma: no cover
                print "appstruct from validation of request.POST:"
                print(appstruct)

            # time to store stuff away...
            if appstruct['name'] != playlist.name:
                # playlist.name was changed
                playlist.name = appstruct['name']

            # TODO: handle the entries in appstruct['entries']

            return HTTPFound(
                route_url('playlist_view', request, playlist_id=playlist.id))
            # show the form with the data again
            #return {
            #    'form': form.render(appstruct)  # , True)
            #    }

        # if form does not validate, show it again with faulty values
        except ValidationFailure, e:
            if DEBUG:  # pragma: no cover
                print "validation must have failed...!"
                print(request.POST.items())
            return {'form': e.render()}

#
#         if form.data['name'] != playlist.name:
#             playlist.name = form.data['name']
#             if DEBUG:  # pragma: no cover
#                 print "changing playlist name"
#                 request.session.flash('changing playlist name')
#
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
