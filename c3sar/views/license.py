from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.url import route_url

#import formencode
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from c3sar.models import (
    DBSession,
    License,
    )

dbsession = DBSession()

##################################################################### license
@view_config(route_name='license',
             permission='view',
             renderer='../templates/license.pt')
def license(request):
    return {'foo': 'bar'}

##################################################################### license_create
@view_config(route_name='license_create',
             permission='view',
             renderer='../templates/license_create.pt')
def license_create(request):

    viewer_username = authenticated_userid(request)
    if viewer_username == "":
        viewer_username = "not logged in"

 #   form = Form(request, LicenseSchema)
    form = Form(request)

    if 'form.submitted' in request.POST and not form.validate():
        # form didn't validate
        request.session.flash('form does not validate!')
        request.session.flash(form.data['license_name'])
        request.session.flash(form.data['license_url'])


    if 'form.submitted' in request.POST and form.validate():
        request.session.flash('form validated!')
        license_name = form.data['license_name']

        license = License(
            license_name = form.data['license_name'],
            license_album = form.data['license_album'],
            license_url = form.data['license_url'],
            )

        dbsession.add(license)
        request.session.flash(u'writing to database ...')

        # ToDo: https://redmine.local/issues/5

    return {
        'viewer_username': viewer_username,
        'form': FormRenderer(form)
        }

##################################################################### license_add
@view_config(route_name='license_add',
             permission='view',
             renderer='../templates/license_add.pt')
def license_add(request):

    viewer_username = authenticated_userid(request)
    request.session.flash(authenticated_userid(request))
    if viewer_username == None:
        viewer_username = "not logged in"

    dbsession = DBSession()

    #form = Form(request, LicenseSchema)
    form = Form(request)


    if 'form.submitted' in request.POST:

        my_results_dict = request.str_POST
        #request.session.flash(my_results_dict.keys())

        #request.session.flash("cc license? " + my_results_dict['cc_js_want_cc_license'])
        #request.session.flash("uri: " + my_results_dict['cc_js_result_uri'])
        #request.session.flash("img: " + my_results_dict['cc_js_result_img'])
        #request.session.flash("name: " + my_results_dict[u'cc_js_result_name'])


        if (my_results_dict['cc_js_want_cc_license'] == 'sure'):
            request.session.flash("we got a cc license...")


            # request.session.flash("license? :" + form.data['cc_js_want_cc_license'])
            # request.session.flash("sharing? :" + form.data['cc_js_share'])
            # request.session.flash("remixing? :" + form.data['cc_js_remix'])
            # request.session.flash("locale :" + form.data['cc_js_jurisdiction'])
            # request.session.flash("URI :" + request.POST.cc_js_result_uri)
            # request.session.flash("img :" + form.data['cc_js_result_img'])
            # request.session.flash("name :" + form.data['cc_js_result_name'])


            license = License(
                name = my_results_dict['cc_js_result_name'],
                uri = my_results_dict['cc_js_result_uri'],
                img = my_results_dict['cc_js_result_img'],
                author = viewer_username
                )

            dbsession.add(license)
            request.session.flash(u'writing to database ...')
            dbsession.flush()

        else:
            request.session.flash("we got an all rights reserved license...")
        
            license = License(
                name = 'All rights reserved',
                uri = '',
                img = '', 
                author = viewer_username
                )
            
            dbsession.add(license)
            request.session.flash(u'writing to database ...')
            dbsession.flush()
        
        # redirect to license_view 
        redirect_url = route_url('license_list', request)
        return HTTPFound(location = redirect_url) 

    return {
        'viewer_username': viewer_username,
        'form': FormRenderer(form)
        }


######################## test url parameters

@view_config(route_name = 'url_param_test',
             renderer = '../templates/url_params_test.pt')
def url_param_test(request):
    """
    get the parameters from the URL and use them as information.
    useful in combination with CC license chooser, accepting a request (the
    rebound) and using a pyramid view as their *exit_url*

    gathering license info and maybe store it
    """

    # get and save the query_string for processing
    params = request.query_string
    # http://docs.pylonsproject.org/projects/pyramid/dev/
    #             narr/webob.html#urls
    #             api/request.html#pyramid.request.Request.query_string


#    request.session.flash(params)

    # check if any
    if params == '':
        url_params = 'None'
        license_name = 'None'
        license_url = 'None'
        return {
            'url_params': url_params,
            'license_name' : license_name,
            'license_url' : license_url,
            'license_image' : None,
            }           
    



    
    # urldecode the string == urllib.unquote
    from urllib import unquote
    params = unquote(params)
    #request.session.flash(params)


    # split up the string for &s and =s, get as dict
    try:
        url_params = dict([part.split('=') for part in params.split('&')])

    except ValueError, v:
        print v
        url_params = ''

    #request.session.flash('license_name' in url_params)
    #request.session.flash(url_params)
    
    # example URL:
    # "http://foo.de/bar/return_from_cc;myParam=moo?license_url=http://creativecommons.org/licenses/by/3.0/&license_name=Creative%20Commons%20Attribution%203.0%20Unported&userID=42%26user-work=foo.jpg#end"
    #
    #request.session.flash(urlparse(url_to_parse))
    # yields:
    # ParseResult(scheme='http', netloc='foo.de', path='/bar/return_from_cc', params='myParam=moo',
    #             query='license_url=http://creativecommons.org/licenses/by/3.0/&license_name=Creative%20Commons%20Attribution%203.0%20Unported&userID=42%26user-work=foo.jpg',
    #             fragment='end')

    from urlparse import urlparse

    the_query = urlparse(params).query

 #   the_split_query = the_query.split("&") # is a list
    #request.session.flash(type(the_split_query)) # is a list

#    for param in the_split_query:
        #request.session.flash(param)
#        p, v = param.split('=')
        
#        print(p, v)
        #request.session.flash(v)
        #if p.startswith()

    if 'license_url' in url_params: license_url = url_params['license_url']
    else: license_url = u'None'
        
    if 'license_img' in url_params: license_img = url_params['license_image'] 
    else: license_img = u'None'
    
    if 'license_name' in url_params: license_name = url_params['license_name'] 
    else: license_name = u'None'

    return {
        'url_params': url_params,
        'the_query': the_query,
#        'the_split_query': the_split_query,
        'license_name' : license_name,
        'license_url' : license_url,
        'license_image' : None,
        }

##################################################################### license_ws_add
# let's try and add a license using the creativecommons.org REST api
# see http://wiki.creativecommons.org/Web_Services

@view_config(route_name='license_add_ws',
             permission='view',
             renderer='../templates/license_add_ws.pt')
def license_add_ws(request):

    viewer_username = authenticated_userid(request)
    request.session.flash(authenticated_userid(request))
    if viewer_username == None:
        viewer_username = "not logged in"

    #form = Form(request, LicenseSchema)
    form = Form(request)


    if 'form.submitted' in request.POST:
        # request.session.flash("Here comes request.str_POST")
        # request.session.flash(request.str_POST)
        # request.session.flash("And this is request.POST")
        # request.session.flash(request.POST)

        my_results_dict = request.str_POST
        request.session.flash(my_results_dict.keys())

        request.session.flash(my_results_dict['cc_js_want_cc_license'])
        request.session.flash(my_results_dict['cc_js_result_uri'])
        request.session.flash(my_results_dict['cc_js_result_img'])
        request.session.flash(my_results_dict[u'cc_js_result_name'])

        # so here is what we need to store:
        #the_license = License(
        #    cc_license = my_results_dict['cc_js_want_cc_license'])

        
        #request.session.flash("license? :" + form.data['cc_js_want_cc_license'])
        # request.session.flash("sharing? :" + form.data['cc_js_share'])
        # request.session.flash("remixing? :" + form.data['cc_js_remix'])
        # request.session.flash("locale :" + form.data['cc_js_jurisdiction'])
#        request.session.flash("URI :" + request.POST.cc_js_result_uri)
        # request.session.flash("img :" + form.data['cc_js_result_img'])
        # request.session.flash("name :" + form.data['cc_js_result_name'])


    
    # if 'form.submitted' in request.POST and not form.validate():
    #     # form didn't validate
    #     request.session.flash('form does not validate!')
    #     request.session.flash(form.data['license_name'])
    #     request.session.flash(form.data['license_url'])


    # if 'form.submitted' in request.POST and form.validate():
    #     request.session.flash('form validated!')
    #     license_name = form.data['license_name']

    #     license = License(
    #         license_name = form.data['license_name'],
    #         license_album = form.data['license_album'],
    #         license_url = form.data['license_url'],
    #         )

    #     dbsession.add(license)
    #     request.session.flash(u'writing to database ...')

    #     # ToDo: https://redmine.local/issues/5

    return {
        'viewer_username': viewer_username,
        'form': FormRenderer(form)
        }


## license_view

@view_config(route_name='license_view',
             permission='view',
             renderer='../templates/license_view.pt')
def license_view(request):

    license_id = request.matchdict['license_id']
    license = License.get_by_license_id(license_id)

    #calculate for next/previous-navigation
    if int(license_id) == 1:
        prev_id = 1
    else:
        prev_id = int(license_id) - 1

    next_id = int(license_id) + 1
    # TODO: MAXiD
    # if license_id == MaxId: next_id = license_id


    # show who is watching. maybe we should log this ;-)
    viewer_username = authenticated_userid(request)



    return {
        'license': license,
        'viewer_username': viewer_username,
        'prev_id': prev_id,
        'next_id': next_id
        }

## license_list
@view_config(route_name='license_list',
             permission='view',
             renderer='../templates/licenses_list.pt')
def license_list(request):
    licenses = License.license_listing(License.id.desc())
    return {'licenses': licenses}

## license_edit
@view_config(route_name='license_edit',
             permission='view',
             renderer='../templates/licenses_edit.pt')
def license_edit(request):
    pass

## license_del
@view_config(route_name='license_del',
             permission='view',
             renderer='../templates/licenses_del.pt')
def license_del(request):
    pass

## license_search
@view_config(route_name='license_search',
             permission='view',
             renderer='../templates/licenses_search.pt')
def license_search(request):
    pass
