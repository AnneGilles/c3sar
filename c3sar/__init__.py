from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from c3sar.models import initialize_sql
from c3sar.models import initialize_s3


# for user sessioning
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    #initialize_s3()
    
    # user sessioning
    session_factory = UnencryptedCookieSessionFactoryConfig('secret')
    authn_policy = AuthTktAuthenticationPolicy('s0secret!!')
    authz_policy = ACLAuthorizationPolicy()


    config = Configurator(settings=settings,
                          authentication_policy = authn_policy,
                          authorization_policy  = authz_policy,
                          session_factory = session_factory,
                          )
    # static view for images and favicon
    config.add_static_view('static', 'c3sar:static')
    config.add_route('home', '/')
    config.add_view('c3sar.views.my_view.my_view',
                    route_name='home',
                    renderer='templates/mytemplate.pt'
                    )

    # prepare to use the base template
    config.add_subscriber('c3sar.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')

    ### user views
    # registration
    config.add_route('register', '/register')
    config.add_view('c3sar.views.user.user_register',
                     route_name='register',
                     renderer='templates/user_register.pt'
                     )

    #config.scan()

    return config.make_wsgi_app()

