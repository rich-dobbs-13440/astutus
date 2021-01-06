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
import os

import astutus.raspi
import astutus.web.flask_app
import astutus.db
import astutus.log
import astutus.util
import astutus.web.usb_pages
import astutus.web.raspi_pages
import flask
import flask.logging

logger = logging.getLogger(__name__)


def create_app_and_db():

    app = flask.Flask('astutus.web.flask_app', template_folder='templates')
    app.config["SQLALCHEMY_DATABASE_URI"] = astutus.db.get_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = astutus.db.get_instance()
    db.init_app(app)
    with app.app_context():
        astutus.db.initialize_db_if_needed()
    app.register_blueprint(astutus.web.raspi_pages.raspi_page)
    astutus.web.raspi_pages.db = db
    app.register_blueprint(astutus.web.usb_pages.usb_page)

    flask.logging.default_handler.setFormatter(astutus.log.standard_formatter)
    global logger
    level_by_logger = {
        astutus.raspi.find.logger: logging.INFO,
        astutus.raspi.raspi_impl.logger: logging.INFO,
        astutus.web.usb_pages.logger: logging.INFO,
        astutus.usb.tree.logger: logging.INFO,
        logger: logging.DEBUG,
    }
    for logger, level in level_by_logger.items():
        logger.addHandler(flask.logging.default_handler)
        logger.setLevel(level)
    return app, db


app, db = create_app_and_db()


wy_menu_vertical_list = [
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc">Welcome</a></li>'
    '<li class="toctree-l1"><a class="reference internal" href="/astutus">Browser Astutus</a></li>'
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc/command_line">Command Line Astutus</a></li>'  # noqa
]
wy_menu_vertical = "\n".join(wy_menu_vertical_list)

static_base = "/static/_docs/_static"


@app.template_filter('tojson_pretty')
def tojson_pretty_jinja2_template_file(json_text):
    parsed_json = json.loads(json_text)
    return json.dumps(parsed_json, indent=4, sort_keys=True)


@app.route('/')
def handle_top():
    """ app.route('/') """
    return flask.redirect(flask.url_for("handle_astutus"))


@app.route('/astutus')
def handle_astutus():

    """ app.route('/astutus') """
    breadcrumbs_list = [
        '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
        '<li>/astutus</li>',
    ]
    breadcrumbs_list_items = "\n".join(breadcrumbs_list)
    links_list = [
        '<li><p>See <a class="reference internal" href="/astutus/raspi"><span class="doc">Raspberry Pi</span></a></p></li>',  # noqa
        '<li><p>See <a class="reference internal" href="/astutus/usb"><span class="doc">USB</span></a></p></li>',  # noqa
    ]
    links = "\n".join(links_list)
    return flask.render_template(
        'transformed_dyn_astutus.html',
        static_base=static_base,
        breadcrumbs_list_items=breadcrumbs_list_items,
        wy_menu_vertical=wy_menu_vertical,
        links=links)


@app.route('/astutus/doc')
def handle_doc():
    """ @app.route('/astutus/doc') """
    return flask.redirect(flask.url_for("handle_doc_top"))


@app.route('/astutus/doc/index.html')
def handle_doc_top():
    """ app.route('/astutus/doc/index.html') """
    logger.debug(f"app.root_path: {app.root_path}")
    directory = os.path.join(app.root_path, 'static', '_docs')
    print(f"directory: {directory}")
    return flask.send_from_directory(directory, 'index.html')


@app.route('/astutus/doc/<path:path>')
def handle_doc_path(path):
    """ app.route('/astutus/doc/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {app.root_path}")
    real_path = os.path.join(app.root_path, 'static', '_docs', path)
    print(f"real_directory: {real_path}")
    return flask.send_file(real_path)


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
