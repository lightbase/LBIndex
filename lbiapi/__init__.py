#!/bin/env python
# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from pyramid.renderers import JSON

from .model.context.command import CommandFactory
from .views.command import CommandView


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('def_json_rend', JSON(indent=2))

    config.add_route(
        'post_cmd_rt', '/', factory=CommandFactory,
        request_method='POST')

    config.add_route(
        'get_cmd_rt', '/', factory=CommandFactory,
        request_method='GET')

    config.add_route(
        'put_cmd_rt', '/', factory=CommandFactory,
        request_method='PUT')

    config.add_route(
        'delete_cmd_rt', '/', factory=CommandFactory,
        request_method='DELETE')

    perms = {
        'GET': 'view',
        'POST': 'create',
        'PUT': 'edit',
        'DELETE': 'delete'
    }

    config.add_view(
        view=CommandView, attr='post_command', route_name='post_cmd_rt',
        request_method='POST', permission=perms['POST'])

    config.add_view(
        view=CommandView, attr='get_command', route_name='get_cmd_rt',
        request_method='GET', permission=perms['GET'])

    config.add_view(
        view=CommandView, attr='put_command', route_name='put_cmd_rt',
        request_method='PUT', permission=perms['PUT'])

    config.add_view(
        view=CommandView, attr='delete_command', route_name='delete_cmd_rt',
        request_method='DELETE', permission=perms['DELETE'])

    config.scan()
    return config.make_wsgi_app()
