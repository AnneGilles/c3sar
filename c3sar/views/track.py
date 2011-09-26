import formencode
from formencode import validators

from pyramid.security import authenticated_userid
from pyramid.url import route_url
from pyramid.view import view_config

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from c3sar.models import Track
from c3sar.models import License
from c3sar.models import DBSession

dbsession = DBSession()

import string

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
    track_name = formencode.validators.String(not_empty = True)
#    track_url = formencode.validators.String(not_empty = True) #works, but no good for urls
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
    if viewer_username == "":
        viewer_username = "not logged in"

    form = Form(request, TrackSchema)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash('name: ' + form.data['track_name'])
        request.session.flash('url: ' + form.data['track_url'])
#        request.session.flash('file: ' + form.data['file'])


    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')

        # some defaults
        file_path = ''
        output_file_size = None

        import pprint
        pp = pprint.PrettyPrinter(depth=6)
        print "---- form.data: ----"
        pp.pprint(form.data)
        print "---- request.POST: ----"
        pp.pprint(request.POST)
        
        print "yes, Im here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
        print str(form.data['track_file'] == '')

        # check if the form contained a file and if yes....
        #if 'track_file' in form.data:
        if form.data['track_file'] != '':
            #request.session.flash('there is a file supplied through the form')
            #request.session.flash('filename: ' + str(form.data['file'].filename))
            #request.session.flash('file: ' + str(form.data['file'].file))

            # https://docs.pylonsproject.org/projects/
            #           pyramid_cookbook/dev/files.html#basic-file-uploads
            #
            # ``filename`` contains the name of the file in string format.
            #
            # WARNING: this example does not deal with the fact that IE sends an
            # absolute file *path* as the filename.  This example is naive; it
            # trusts user input.

            filename = sanitize_filename(request.POST['file'].filename)

            # ``input_file`` contains the actual file data which needs to be
            # stored somewhere.

            input_file = request.POST['file'].file

            # Using the filename like this without cleaning it is very
            # insecure so please keep that in mind when writing your own
            # file handling.
            import os

            file_path = os.path.join('c3sar/tracks', filename)
            output_file = open(file_path, 'wb')

            # Finally write the data to the output file
            input_file.seek(0)
            while True:
                data = input_file.read(8192)
                if not data:
                    break
                output_file.write(data)

            # determining filesize
            import os
            output_file_size = os.path.getsize(file_path)

            output_file.close()


            request.session.flash('Upload went well!')
            #return Response('OK')


        dbsession = DBSession()
        name = form.data['track_name']

        if file_path.startswith('c3sar/'):
            file_path = file_path.replace('c3sar/', '')


        track = Track(
            name = form.data['track_name'],
            album = form.data['track_album'],
            url = form.data['track_url'],
            #file = form.data['track_file'],
            filepath = file_path,
            bytesize = output_file_size,
            )



        dbsession.add(track)
        dbsession.flush() # to get track.id
        print "---- DEBUG ---- " + str(track.id)
        request.session.flash(u'writing to database ...')

        # ToDo: send user to track_view/this_id
        # ToDo: send mail...

        
        #redirect_url = route_url('track_list', request)
        redirect_url = route_url('track_view', request, track_id=track.id) #+ str(track.id)
        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location = redirect_url)

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
    #license = track.license[1]
#    request.session.flash(track.license[0])
#    request.session.flash(track.license[1])
    # who is doing this?
    viewer_username = authenticated_userid(request)

    form = Form(request) 

    DEBUG = True
    if DEBUG:
        import pprint
        pp = pprint.PrettyPrinter(depth=6)

    if 'form.submitted' in request.POST:
        # request.session.flash("Here comes request.str_POST")
        # request.session.flash(request.str_POST)
        # request.session.flash("And this is request.POST")
        # request.session.flash(request.POST)

        my_results_dict = request.str_POST
        #request.session.flash(my_results_dict.keys())

        if DEBUG:
            print "===== DEBUG ===== DEBUG ===== DEBUG ====="
            pp.pprint(my_results_dict.keys())
            pp.pprint(my_results_dict['cc_js_want_cc_license'])

            
            # request.session.flash("cc license? " + my_results_dict['cc_js_want_cc_license'])
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
                    name = my_results_dict['cc_js_result_name'],
                    uri = my_results_dict['cc_js_result_uri'],
                    img = my_results_dict['cc_js_result_img'],
                    author = viewer_username
                    )
                                     )
                #                dbsession.add(license) # no, add via track
                #                dbsession.add(track) # no, don't add, just update
                request.session.flash(u'writing to database ... by flush')
                dbsession.flush()
                
            else:
                request.session.flash("we got an all rights reserved license...")
                
                track.license = License(
                    name = 'All rights reserved',
                    uri = '',
                    img = '', 
                    author = viewer_username
                    )
                
                request.session.flash(u'writing to database ... by flushing')
                dbsession.flush()
        
        # redirect to license_view
        redirect_url = route_url('track_view', request, track_id=str(track.id)) #+ str(track.id)
        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location = redirect_url)

        
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

    id = request.matchdict['track_id']
    track = Track.get_by_track_id(id)

    # catch Error if id /not /exists
    try:
        print "===== track.id: " + str(track.id)
        print "===== track.license.__len__(): " + str(track.license.__len__())
    except AttributeError, a:
        #'NoneType' object has no attribute 'license'
        print "========================================================="
        print "========================================================="
        print a
        print "========================================================="
        print "========================================================="
        # here we should redirect to NotFound or give some info

        
    #calculate for next/previous-navigation
    if int(id) == 1:
        prev_id = 1
    else:
        prev_id = int(id) - 1

    next_id = int(id) + 1
    # TODO: MAXiD
    # if track_id == MaxId: next_id = track_id


    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)
#    request.session.flash("track.license.__len__(): " + str(track.license.__len__()))
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
        request.session.flash("track.license.name: " + str(track.license[0].img))
        

    print "===================================="
    print "str(type(track.license)): " + str(type(license))
    print "===================================="
    print "str(dir(track.license)): " + str(dir(license))
    print "===================================="
#    print "str(help(track.license.pop())): " + str(help(track.license.pop()))
    print "===================================="
    print "str(type(license)): " + str(type(license))
    print "===================================="
#    print "str(type(license.name)): " + str(type(license.name))
    print "===================================="
#    print str(dir(license))
#    print "===================================="
#    print str(license.name)
    print "===================================="
        
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

## track_edit
@view_config(route_name='track_edit',
             permission='view',
             renderer='../templates/track_edit.pt')
def track_edit(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}

## track_del
@view_config(route_name='track_del',
             permission='view',
             renderer='../templates/track_del.pt')
def track_del(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}

## track_search
@view_config(route_name='track_search',
             permission='view',
             renderer='../templates/track_search.pt')
def track_search(request):
    tracks = Track.track_listing(Track.id.desc())
    return {'tracks': tracks}
