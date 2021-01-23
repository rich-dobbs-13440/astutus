#!/usr/bin/env python3
"""

This module implements the Flask web application for the package.

The web application provides:

    * A server for the Sphinx generated documentation.
    * An HTML interface for interacting with the system.
    * A REST API for interacting with the system remotely
    * or locally for automation.

The handle routines are all Flask endpoints.

Maintainence note:

    Include the app.route decorator in the docstrings
    for the handle routines.

"""
import json
import logging
import sqlite3
# from http import HTTPStatus

import astutus.db
import astutus.log
import astutus.raspi
import astutus.util
import astutus.web.flask_app
import astutus.web.log_pages
import astutus.web.raspi_pages
import astutus.web.usb_pages
import astutus.web.doc_pages
import flask
import flask.logging

logger = logging.getLogger(__name__)


def create_app_and_db(static_base):

    try:
        app = flask.Flask('astutus.web.flask_app', template_folder='templates')
        app.config["SQLALCHEMY_DATABASE_URI"] = astutus.db.get_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = astutus.db.get_instance()
        db.init_app(app)
        with app.app_context():
            astutus.db.initialize_db_if_needed()
            app.register_blueprint(astutus.web.raspi_pages.raspi_page)
            astutus.web.raspi_pages.db = db
            astutus.web.raspi_pages.static_base = static_base
            app.register_blueprint(astutus.web.usb_pages.usb_page)
            astutus.web.usb_pages.static_base = static_base
            app.register_blueprint(astutus.web.log_pages.log_page)
            astutus.web.log_pages.static_base = static_base
            astutus.web.log_pages.db = db
            app.register_blueprint(astutus.web.doc_pages.doc_page)
            astutus.web.doc_pages.doc_page.root_path = app.root_path
            # Handle logging configuration
            flask.logging.default_handler.setFormatter(astutus.log.standard_formatter)
            level_by_logger_name = {}
            for item in astutus.db.Logger.query.all():
                level_by_logger_name[item.name] = item.level
            for logger in astutus.log.get_loggers():
                logger.addHandler(flask.logging.default_handler)
                level = level_by_logger_name.get(logger.name, logging.WARNING)
                logger.setLevel(level)
            return app, db
    except sqlite3.OperationalError as exception:
        logger.error(exception)
    raise RuntimeError("Please delete out-of-date database.")


static_base = "/static/_docs/_static"
app, db = create_app_and_db(static_base=static_base)


@app.template_filter('tojson_pretty')
def tojson_pretty_jinja2_template_file(json_text):
    logger.debug(f"json_text: {json_text}")
    parsed_json = json.loads(json_text)
    return json.dumps(parsed_json, indent=2, sort_keys=True)


@app.route('/')
def handle_top():
    """ app.route('/') """
    return flask.redirect(flask.url_for("handle_astutus"))


@app.route('/astutus/app/dyn_index.html', methods=['GET'])
def handle_app_index_from_doc():
    return flask.redirect(flask.url_for("handle_astutus"))


@app.route('/astutus/app/index.html')
def handle_astutus():

    """ app.route('/astutus') """
    breadcrumbs_list = [
        '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
        '<li>/astutus</li>',
    ]
    breadcrumbs_list_items = "\n".join(breadcrumbs_list)
    links_list = [
        '<li><p>Control the <a class="reference internal" href="/astutus/log">logging</a> in the web application.</p></li>'  # noqa
        '<li><p>Discover and work with <a class="reference internal" href="/astutus/app/raspi"><span class="doc">Raspberry Pi\'s</span> on your system</a></p></li>',  # noqa
        '<li><p>Understand the <a class="reference internal" href="/astutus/app/usb"><span class="doc">USB devices</span></a> on you system</p></li>',  # noqa
    ]
    links = "\n".join(links_list)
    return flask.render_template(
        'dyn_index.html',
        static_base=static_base,
        breadcrumbs_list_items=breadcrumbs_list_items,
        links=links)


def run_with_standard_options():
    external_visible = "0.0.0.0"
    app.run(
        host=external_visible,
        port=5000,
        # use_debugger=True,
        # use_evalex=False,
    )


if __name__ == '__main__':
    astutus.web.flask_app.run_with_standard_options()
