from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from c3sar.models import initialize_sql
#from c3sar.models import initialize_s3
from c3sar.security.request import RequestWithUserAttribute
from c3sar.security import groupfinder
from c3sar.security import (
    Root,
    UserFactory,
#    BandFactory,
    TrackFactory,
#    LicenseFactory,
#    PlaylistFactory,
    )
# for user sessioning
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
# user sessioning with pyramid_beaker
from pyramid_beaker import session_factory_from_settings


def includeme(config):
    """
        Registers a c3sar instance.

        :versionadded: 0.4
        """
    pass
#    settings = config.registry.settings
#    prefix = settings.get('c3sar.prefix', 'c3sar.')
#    c3sar = mailer_factory_from_settings(settings, prefix=prefix)
#    config.registry.registerUtility(mailer, IMailer)


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')

    initialize_sql(engine)
    #initialize_s3()

    # user sessioning: beaker
    session_factory = session_factory_from_settings(settings)
    authn_policy = AuthTktAuthenticationPolicy('s0secret!!',
                                               callback=groupfinder,
                                               )
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory,
                          root_factory=Root,
                          )

    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)

    # static view for images and favicon
    config.add_static_view('static', 'c3sar:static')
    config.add_route('home', '/')
    config.add_view('c3sar.views.basic.home_view',
                    route_name='home',
                    renderer='templates/main.pt'
                    )
    config.add_route('favicon.ico', '/favicon.ico')
    config.add_view('c3sar.views.basic.favicon_view',
                    route_name='favicon.ico')
    # config.add_view('c3sar.views.my_view.my_view',
    #                 route_name='home',
    #                 renderer='templates/mytemplate.pt'
    #                 )

    # general 403: used when lacking some permission
    # overrides builtin 403 forbidden_view
    from pyramid.httpexceptions import HTTPForbidden
    #from c3sar.views.basic import not_allowed_view
    config.add_view('c3sar.views.basic.not_allowed_view',
                    context=HTTPForbidden,
                    renderer='templates/not_allowed.pt')

    # not needed as of now: route and view for 403, see above
    #config.add_route('not_allowed', '/not_allowed')
    #config.add_view('c3sar.views.basic.not_allowed_view',
    #                    route_name='not_allowed',
    #                    renderer='templates/not_allowed.pt')

    # about
    config.add_route('about', '/about')
    config.add_view('c3sar.views.basic.about_view',
                    route_name='about',
                    renderer='templates/about.pt'
                    )
    # listen
    config.add_route('listen', '/listen')
    config.add_view('c3sar.views.basic.listen_view',
                    route_name='listen',
                    renderer='templates/listen.pt'
                    )

    # not implemented
    config.add_route('not_implemented', '/not_implemented')
    config.add_view('c3sar.views.basic.not_implemented_view',
                    route_name='not_implemented',
                    renderer='templates/not_implemented.pt'
                    )

    # general 404: catchall if not found / wrong URL
    from pyramid.httpexceptions import HTTPNotFound
    from c3sar.views.basic import notfound_view
    config.add_view(notfound_view, context=HTTPNotFound)

    # special 404: not found view to redirect to
    config.add_route('not_found', '/not_found')
    config.add_view('c3sar.views.basic.not_found_view',
                    route_name='not_found',
                    renderer='templates/not_found.pt'
                    )

    # prepare to use the base template
    config.add_subscriber('c3sar.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')

    ### user views / routes ##
    # user registration / create /add
    config.add_route('register', '/register')
    config.add_view('c3sar.views.user.user_register',
                    route_name='register',
                    permission='registerUser',
                    renderer='templates/user_add.pt'
                    )
    # user confirm_email
    config.add_route('confirm_email',
                     '/user/confirm/{code}/{user_name}/{user_email}')
    config.add_view('c3sar.views.user.user_confirm_email',
                    route_name='confirm_email',
                    renderer='templates/user_confirm_email.pt')

    # user index
    config.add_route('user_list', '/user/list')
    config.add_view('c3sar.views.user.user_list',
                    route_name='user_list',
                    renderer='templates/user_list.pt')
    # user view
    config.add_route('user_view', '/user/view/{user_id}')
    config.add_view('c3sar.views.user.user_view',
                    route_name='user_view',
                    renderer='templates/user_view.pt')

    # user profile -- mostly for self-service
    config.add_route('user_profile', '/user/profile/{user_id}')
    config.add_view('c3sar.views.user.user_profile',
                    route_name='user_profile',
                    renderer='templates/user_profile.pt')

    # user edit
    config.add_route('user_edit_no_id', '/user/edit')  # if no id appended
    config.add_view('c3sar.views.user.user_edit',
                    route_name='user_edit_no_id',
                    renderer='templates/user_edit_table.pt')

    config.add_route('user_edit',
                     '/user/edit/{user_id}',
                     factory=UserFactory,
                     traverse='/{user_id}')
    #config.add_route('user_edit', '/user/edit/{user_id}',
    #                 traverse='/{user_id}')
    #config.add_route('user_edit', '/user/edit/{user_id}',
    #                 factory=UserContainer,
    #                 )
    config.add_view('c3sar.views.user.user_edit',
                    route_name='user_edit',
                    #permission='editUser',  # now managed in the view!
                    renderer='templates/user_edit_table.pt')

    # delete
    #config.add_route('user_del', '/user/rm')
    # search
    #config.add_route('user_search', '/users/search/')

    # user log in
    config.add_route('login', '/login')
    config.add_view('c3sar.views.user.login_view',
                    route_name='login',
                    renderer='templates/user_login.pt')
    # user log out
    config.add_route('logout', '/logout')
    config.add_view('c3sar.views.user.logout_view',
                    route_name='logout',
                    renderer='templates/user_login.pt')
    # user set default license
    config.add_route('user_set_default_license',
                     '/user/set_default_license/{user_id}')
    # config.add_route('user_edit',
    #                  '/user/edit/{user_id}', traverse='/{user_id}')
    #config.add_route('user_edit', '/user/edit/{user_id}',
    #                 factory=UserContainer,
    #                 )
    config.add_view('c3sar.views.user.user_set_default_license',
                    route_name='user_set_default_license',
                    renderer='templates/user_set_default_license.pt')

    # user get contract with username in filename
    config.add_route('user_contract_de_username',
                     '/user/bv/C3S_contract_{username}.pdf')
    config.add_view('c3sar.views.user.user_contract_de_username',
                    route_name='user_contract_de_username')

    config.add_route('user_login_first',
                     '/sign_in_first')
    config.add_view('c3sar.views.user.user_login_first',
                    route_name='user_login_first',
                    renderer='templates/have_to_login.pt')

    ## routes for bands ##
    # band create
    config.add_route('band_add', '/band/add')
    #config.add_route('band_add', '/band/add',
    #factory=BandContainer)
    config.add_view('c3sar.views.band.band_add',
                    route_name='band_add',
                    renderer='templates/band_add.pt')
    # band index
    config.add_route('band_list', '/band/list')
    config.add_view('c3sar.views.band.band_list',
                    route_name='band_list',
                    renderer='templates/band_list.pt')
    # band view
    config.add_route('band_view', '/band/view/{band_id}')
    config.add_view('c3sar.views.band.band_view',
                    route_name='band_view',
                    renderer='templates/band_view.pt')
    # band edit / settings
    config.add_route('band_edit', '/band/edit/{band_id}')
    config.add_view('c3sar.views.band.band_edit',
                    route_name='band_edit',
                    renderer='templates/band_edit.pt')
    # band delete
#    config.add_route('band_del', '/band/rm/{band_id}')
#    config.add_view('c3sar.views.band.band_del',
#                    route_name='band_del',
#                    renderer='templates/band_del.pt')
    # search
#    config.add_route('band_search', '/band/search')
#    config.add_view('c3sar.views.band.band_search',
#                    route_name='band_add',
#                    renderer='templates/band_search.pt')

    ## routes for tracks ##
    # track create
    config.add_route('track_add', '/track/add',
                     factory=TrackFactory,
                     )
    config.add_view('c3sar.views.track.track_add',
                    route_name='track_add',
                    permission='addTrack',
                    renderer='templates/track_add.pt')
    # track index
    config.add_route('track_list', '/track/list',
                     factory=TrackFactory)
    config.add_view('c3sar.views.track.track_list',
                    route_name='track_list',
                    #permission='viewTrack',
                    renderer='templates/track_list.pt')
    # view
    config.add_route('track_view', '/track/view/{track_id}',
                     factory=TrackFactory)
    config.add_view('c3sar.views.track.track_view',
                    route_name='track_view',
                    #permission='viewTrack',
                    renderer='templates/track_view.pt')
    # edit
    config.add_route('track_edit', '/track/edit/{track_id}',
                     factory=TrackFactory,
                     traverse='/{track_id}'
                     )
    config.add_view('c3sar.views.track.track_edit',
                    route_name='track_edit',
                    permission='editTrack',
                    renderer='templates/track_edit.pt')

    # track: add license
    config.add_route('track_add_license', '/track/add_license/{track_id}')
    config.add_view('c3sar.views.track.track_add_license',
                    route_name='track_add_license',
                    renderer='templates/track_add_license.pt')

    # delete
    config.add_route('track_del', '/track/rm/{track_id}')
    config.add_view('c3sar.views.track.track_del',
                    route_name='track_del',
                    renderer='templates/track_del.pt')
    # search
    config.add_route('track_search', '/track/search')
    config.add_view('c3sar.views.track.track_search',
                    route_name='track_search',
                    renderer='templates/track_search.pt')

    ## routes for licenses ##
    # blank / info
    config.add_route('license_', '/license/')
    config.add_view('c3sar.views.license.license',
                    route_name='license_',
                    renderer='templates/license.pt')
    config.add_route('license', '/license')
    config.add_view('c3sar.views.license.license',
                    route_name='license',
                    renderer='templates/license.pt')
    # create
    config.add_route('license_create', '/license/create')
    config.add_view('c3sar.views.license.license_create',
                    route_name='license_create',
                    renderer='templates/license_create.pt')
    # add (to something)
    config.add_route('license_add', '/license/add')
    config.add_view('c3sar.views.license.license_add',
                    route_name='license_add',
                    renderer='templates/license_add.pt')
    # index
    config.add_route('license_list', '/license/list')
    config.add_view('c3sar.views.license.license_list',
                    route_name='license_list',
                    renderer='templates/license_list.pt')
    # view
    config.add_route('license_view', '/license/view/{license_id}')
    config.add_view('c3sar.views.license.license_view',
                    route_name='license_view',
                    renderer='templates/license_view.pt')
    # edit / settings
    config.add_route('license_edit', '/license/edit/{license_id}')
    config.add_view('c3sar.views.license.license_edit',
                    route_name='license_edit',
                    renderer='templates/not_implemented.pt')
    # delete
    config.add_route('license_del', '/license/rm/{license_id}')
    config.add_view('c3sar.views.license.license_del',
                    route_name='license_del',
                    #renderer='templates/license_del.pt')
                    renderer='templates/not_implemented.pt')
    # search
    config.add_route('license_search', '/license/search')
    config.add_view('c3sar.views.license.license_search',
                    route_name='license_search',
                    renderer='templates/license_search.pt')

    ## routes for RESTful interface ##
    config.add_route('api_get_user', '/api/get/user/{id}')
    config.add_view('c3sar.views.rest.show_user_view',
                    route_name='api_get_user',
                    renderer='json',
                    )

    config.add_route('api_report_single_airplay',
                     '/api/report/v1/air/single/{the_report}')
    config.add_view('c3sar.views.reporting_api.reporting_single_airplays_view',
                    route_name='api_report_single_airplay',
                    renderer='json',
                    )

    ##
    config.add_route('url_param_test', '/url_param_test')
    config.add_view('c3sar.views.license.url_param_test',
                    route_name='url_param_test',
                    renderer='templates/url_params_test.pt')

    #config.scan()
    return config.make_wsgi_app()
