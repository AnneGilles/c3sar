import os
import formencode
#from formencode import validators

from pyramid.security import authenticated_userid
from pyramid.url import route_url
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from c3sar.models import (
    Track,
    License,
    DBSession,
    )

dbsession = DBSession()

DEBUG = False
#DEBUG = True

if DEBUG:  # pragma: no cover
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

# validator for track: URL or file upload #####################################
# class URLorFile(validators.FancyValidator):
#     def _to_python(self, track_url, track_file, state):
#         if track_url is '' and track_file is '':
#             raise formencode.Invalid(
#                 'URLorFile barks!',
#                 track_url, track_file, state)
#         elif track_url is not None and track_file is not None:
#             raise formencode.Invalid(
#                 'only one please!',
#                 track_url, track_file, state)
#         elif track_url is not None and track_file is None:
#             return track_url
#         elif track_url is None and track_file is not None:
#             return track_file


# formencode schema for Tracks ################################################
class TrackSchema(formencode.Schema):
    allow_extra_fields = True
    track_name = formencode.validators.String(not_empty=True)
    #    track_url = formencode.validators.String(
    #                           not_empty=True) #works, but no good for urls
    #    track_url = formencode.All(
    #     validators.String(not_empty = True),
    #         validators.URL(),
    #     #URLorFile()
    #         )
    #track_file = formencode.validators.FieldStorageUploadConverter()
    #    track_file = formencode.All(
    #        validators.FieldStorageUploadConverter(),
    #        #validators.FileUploadKeeper()
    #        )
    #              FileUploadKeeper
    # see  site-packages/FormEncode-1.2.4-py2.6.egg/formencode/validators.py
    #    # check that we ger *either* URL *or* file ######################
    #    chained_validators = [
    #        URLorFile()
    #        ]


### sanitize file names before upload ###################
# http://stackoverflow.com/questions/295135/
#                          turn-a-string-into-a-valid-filename-in-python#295466
def sanitize_filename(value):
    """
    Normalizes string, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import string
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    value = value.replace(" ", "_")
    value = ''.join(c for c in value if c in valid_chars)
    return value


## track_add
@view_config(route_name='track_add',
             permission='view',
             renderer='../templates/track_add.pt')
def track_add(request):

    viewer_username = authenticated_userid(request)
    if viewer_username == "":  # pragma: no cover
        viewer_username = "not logged in"

    form = Form(request, TrackSchema)

    if DEBUG:  # pragma: no cover
        if 'form.submitted' in request.POST:
            if 'track_name' in form.data:
                print "track_name : " + form.data['track_name']
            if 'track_album' in form.data:
                print "track_album: " + form.data['track_album']
            if 'track_url' in form.data:
                print "track_url  : " + form.data['track_url']
            if 'track_upload' in form.data:
                print "track_upload : " + form.data['track_upload']
                print "track_upload.filename : "
                + form.data['track_upload'].filename
                print "track_upload.file : "
                + form.data['track_upload'].file

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')

    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')

        # some defaults
        file_path = ''           # where the file is stored (incl. name)
        output_file_size = None  # the size of the file

        if DEBUG:  # pragma: no cover
            print "---- form.data: ----"
            pp.pprint(form.data)
            print "---- request.POST['track_file']: ----"
            if 'track_upload' in request.POST:
                pp.pprint(request.POST['track_upload'])
                pp.pprint(request.POST['track_upload'].filename)
                pp.pprint(request.POST['track_upload'].file)
#request.POST['track_upload']    FieldStorage(u'track_upload', u'blahblah.mp3')
#request.POST['track_upload'].filename                          u'blahblah.mp3'
#request.POST['track_upload'].file    <open file '<fdopen>', mode 'w+b' at ...>
            else:
                print "no 'track_upload' in request.POST"

        # check if the form contained a file and if yes....
        if 'track_upload' in form.data and form.data['track_upload'] != '':

            # https://docs.pylonsproject.org/projects/
            #           pyramid_cookbook/dev/files.html#basic-file-uploads
            #
            # ``filename`` contains the name of the file in string format.
            #
            #WARNING: this example does not deal with the fact that IE sends an
            # absolute file *path* as the filename.  This example is naive; it
            # trusts user input.

            file_name = sanitize_filename(
                request.POST['track_upload'].filename)

            # ``input_file`` contains the actual file data which needs to be
            # stored somewhere.

            input_file = request.POST['track_upload'].file

            # Using the filename like this without cleaning it is very
            # insecure so please keep that in mind when writing your own
            # file handling. TODO !!!

            if DEBUG:  # pragma: no cover
                print "=== current working dir: " + os.path.abspath('.')
                print "=== upload target dir: " + os.path.abspath('tracks')

            # prepare to save the file
            the_cwd = os.path.abspath('.')
            file_dir = os.path.join(the_cwd, 'tracks')

            # create a directory for tracks on the filesystem
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)  # pragma: no cover

            file_path = os.path.join(file_dir, file_name)

            try:
                output_file = open(file_path, 'wb')

                # Finally write the data to the output file
                input_file.seek(0)
                while True:
                    data = input_file.read(8192)
                    if not data:
                        break
                    output_file.write(data)

                # determining filesize
                output_file_size = os.path.getsize(file_path)

                output_file.close()

                request.session.flash('file was saved')
                # return Response('OK')
            except IOError, ioerr:  # pragma: no cover
                print "==== got an error ===="
                print ioerr
                print "something failed."

        dbsession = DBSession()

#        if file_path.startswith('c3sar/'):
#            file_path = file_path.replace('c3sar/', '')

        track = Track(
            name=unicode(form.data['track_name']),
            album=unicode(form.data['track_album']),
            url=unicode(form.data['track_url']),
            filepath=unicode(file_path),
            bytesize=output_file_size,
            )

        dbsession.add(track)
        dbsession.flush()

         # ToDo: send mail...

        redirect_url = route_url('track_view', request, track_id=track.id)
        return HTTPFound(location=redirect_url)

    return {
        'viewer_username': viewer_username,
        'form': FormRenderer(form)
        }


## track: add license
@view_config(route_name='track_add_license',
             permission='view',
             renderer='../templates/track_add_license.pt')
def track_add_license(request):
    # which one?
    id = request.matchdict['track_id']
    track = Track.get_by_track_id(id)
    # license = track.license[1]
    # request.session.flash(track.license[0])
    # request.session.flash(track.license[1])
    # who is doing this?
    viewer_username = authenticated_userid(request)

    form = Form(request)

    if 'form.submitted' in request.POST:
        request.session.flash("And this is request.POST")
        request.session.flash(request.POST)

        my_results_dict = request.POST
        #request.session.flash(my_results_dict.keys())
        #pp.pprint(my_results_dict)

        if 'cc_js_want_cc_license' in my_results_dict:
            if DEBUG:  # pragma: no cover
                print "====="
                pp.pprint(my_results_dict.keys())
                pp.pprint(my_results_dict['cc_js_want_cc_license'])

            # request.session.flash("cc license? "
            #        + my_results_dict['cc_js_want_cc_license'])
            # request.session.flash(my_results_dict['cc_js_result_uri'])
            # request.session.flash(my_results_dict['cc_js_result_img'])
            # request.session.flash(my_results_dict[u'cc_js_result_name'])

            if (my_results_dict['cc_js_want_cc_license'] == 'sure'):
                request.session.flash("we got a cc license...")

                # track.license = [
                #     License(
                #         name = my_results_dict['cc_js_result_name'],
                #         uri = my_results_dict['cc_js_result_uri'],
                #         img = my_results_dict['cc_js_result_img'],
                #         author = viewer_username
                #         )
                #     ]
                track.license.append(License(
                    name=my_results_dict['cc_js_result_name'],
                    uri=my_results_dict['cc_js_result_uri'],
                    img=my_results_dict['cc_js_result_img'],
                    author=viewer_username
                    )
                                     )
                #    dbsession.add(license) # no, add via track
                #    dbsession.add(track) # no, don't add, just update
                request.session.flash(u'writing to database ... by flush')
                dbsession.flush()
            elif (my_results_dict['cc_js_want_cc_license'] == 'nah'):
                request.session.flash("got an all rights reserved license...")
                track.license.append(License(
                        name=u'All rights reserved',
                        uri=u'',
                        img=u'',
                        author=viewer_username
                        ))
                request.session.flash(u'writing to database ... by flushing')
                dbsession.flush()
        # redirect to license_view
        redirect_url = route_url('track_view', request, track_id=str(track.id))
        #      + str(track.id)
        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location=redirect_url)

    return {
        'viewer_username': viewer_username,
        'track_id': id,
        'track': track,
        'license': license,
        'form': FormRenderer(form)
        }


## track_view
@view_config(route_name='track_view',
             permission='view',
             renderer='../templates/track_view.pt')
def track_view(request):
    if DEBUG:  # pragma: no cover
        print "============  T R A C K ==  V I E W =========================="
    id = request.matchdict['track_id']
    track = Track.get_by_track_id(id)

    # import pdb; pdb.set_trace()
    # redirect if id does not exist in database
    if not isinstance(track, Track):
        msg = "the track does not exist in the database!"
        return HTTPFound(route_url('not_found', request))
#     try:
#         print "== track.id: " + str(track.id)
#         print "== track.license.__len__(): " + str(track.license.__len__())
#     except AttributeError, a:
#         #'NoneType' object has no attribute 'license'
#         print "== AttributeError: "
#         print a
        # here we should redirect to NotFound or give some info

    #calculate for next/previous-navigation
    max_id = Track.get_max_id()
    # previous
    if track.id == 1:             # if looking at first id
        prev_id = max_id          # --> choose highest db row
    else:                         # if looking at any other id
        prev_id = track.id - 1    # --> choose previous
    # next
    if track.id != max_id:        # if not on highest id
        next_id = track.id + 1    # --> choose next
    elif track.id == max_id:      # if highest id
        next_id = 1               # --> choose first id ('wrap around'))

    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)
    #request.session.flash(
    #          "track.license.__len__(): " + str(track.license.__len__()))
    #request.session.flash("track.license.name: " + track.license[0].name)

    if track.license.__len__() == 0:
        track_is_licensed = False
        license = License(name=u"All Rights Reserved.",
                          uri=u"", img=u"", author=u"default license")
        request.session.flash("track_is_licensed: " + str(track_is_licensed))
    else:
        track_is_licensed = True
        license = track.license[0]
        request.session.flash("track_is_licensed: " + str(track_is_licensed))
        request.session.flash(
            "track.license.name: " + str(track.license[0].img))

    if DEBUG:  # pragma: no cover

        print "str(type(track.license)): " + str(type(license))
        print "str(dir(track.license)): " + str(dir(license))
        # print "str(help(track.license.pop())): "
        # + str(help(track.license.pop()))
        print "str(type(license)): " + str(type(license))
        # print "str(type(license.name)): " + str(type(license.name))
        # print str(dir(license))
        # print str(license.name)

    return {
        'track': track,
        'track_is_licensed': track_is_licensed,
        'license': license,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'id': id,
        'next_id': next_id
        }


## track_list
@view_config(route_name='track_list',
             permission='view',
             renderer='../templates/track_list.pt')
def track_list(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}


## track_edit # TODO
@view_config(route_name='track_edit',
             permission='view',
             renderer='../templates/track_edit.pt')
def track_edit(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}


## track_del # TODO
@view_config(route_name='track_del',
             permission='view',
             renderer='../templates/track_del.pt')
def track_del(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}


## track_search #TODO
@view_config(route_name='track_search',
             permission='view',
             renderer='../templates/track_search.pt')
def track_search(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}
