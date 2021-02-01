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
import astutus.web.app_pages
import astutus.web.log_pages
import astutus.web.raspi_pages
import astutus.web.usb_pages
import astutus.web.doc_pages
import flask
import flask.logging

logger = logging.getLogger(__name__)


def create_app_and_db():

    try:
        app = flask.Flask('astutus.web.flask_app', template_folder='templates')
        app.config["SQLALCHEMY_DATABASE_URI"] = astutus.db.get_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # seconds - 5 minutes
        db = astutus.db.get_instance()
        db.init_app(app)
        with app.app_context():
            astutus.db.initialize_db_if_needed()
            app.register_blueprint(astutus.web.raspi_pages.raspi_page)
            astutus.web.raspi_pages.db = db
            app.register_blueprint(astutus.web.usb_pages.usb_page)
            app.register_blueprint(astutus.web.log_pages.log_page)
            astutus.web.log_pages.db = db
            app.register_blueprint(astutus.web.doc_pages.doc_page)
            astutus.web.doc_pages.doc_page.root_path = app.root_path
            app.register_blueprint(astutus.web.app_pages.app_page)
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


app, db = create_app_and_db()


@app.template_filter('tojson_pretty')
def tojson_pretty_jinja2_template_file(arg):
    if isinstance(arg, dict):
        dumpable = arg
    else:
        dumpable = json.loads(arg)
    return json.dumps(dumpable, indent=2, sort_keys=True)


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
