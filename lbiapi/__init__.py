from pyramid.config import Configurator

from .model.context.command import CommandFactory
from .views.command import CommandView


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route(
        'home', '/', factory=CommandFactory,
        request_method='GET')

    perms = {
        'GET': 'view',
        'POST': 'create',
        'PUT': 'edit',
        'DELETE': 'delete'
    }

    config.add_view(
        view=CommandView, attr='get_command', route_name='home',
        request_method='GET', permission=perms['GET'])

    config.scan()
    return config.make_wsgi_app()
