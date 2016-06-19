# -*- coding: utf8 -*-
"""Main module for libcrowds-analyst."""

import os
from libcrowds_analyst import default_settings
from flask import Flask, request
from flask_wtf.csrf import CsrfProtect
from libcrowds_analyst import view, auth


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(default_settings)
    app.config.from_envvar('LIBCROWDS_ANALYST_SETTINGS', silent=True)
    if not os.environ.get('LIBCROWDS_ANALYST_SETTINGS'):  # pragma: no cover
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)
    setup_csrf(app)
    setup_url_rules(app)
    setup_auth(app)
    return app


def setup_csrf(app):
    """Setup csrf protection."""
    csrf = CsrfProtect(app)
    csrf.exempt(view.index)


def setup_url_rules(app):
    """Setup URL rules"""
    rules = {'/': view.index,
             '/<short_name>': view.analyse_empty_result,
             '/<short_name>/<int:result_id>/edit': view.edit_result,
             '/<short_name>/reanalyse': view.reanalyse}
    for route, func in rules.items():
        app.add_url_rule(route, view_func=func, methods=['GET', 'POST'])


def setup_auth(app):
    """Setup basic auth for all requests."""
    @app.before_request
    def requires_auth():
        if request.endpoint == 'index' and request.method == 'POST':
            return
        creds = request.authorization
        if not creds or not auth.check_auth(creds.username, creds.password):
            return auth.authenticate()