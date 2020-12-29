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
from http import HTTPStatus

import astutus.raspi
import astutus.web.flask_app
import astutus.db
import astutus.log
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_app_and_db():

    app = flask.Flask('astutus.web.flask_app', template_folder='templates')
    app.config["SQLALCHEMY_DATABASE_URI"] = astutus.db.get_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = astutus.db.get_instance()
    db.init_app(app)
    with app.app_context():
        astutus.db.initialize_db_if_needed()
    return app, db


app, db = create_app_and_db()


flask.logging.default_handler.setFormatter(astutus.log.standard_formatter)
astutus.raspi.find.logger.addHandler(flask.logging.default_handler)
astutus.raspi.raspi_impl.logger.addHandler(flask.logging.default_handler)
logger.addHandler(flask.logging.default_handler)


@app.template_filter('tojson_pretty')
def tojson_pretty_jinja2_template_file(json_text):
    parsed_json = json.loads(json_text)
    return json.dumps(parsed_json, indent=4, sort_keys=True)


@app.route('/')
def handle_top():
    """ app.route('/') """
    return "TODO: redirect to /astutus"


@app.route('/astutus')
def handle_astutus():
    """ app.route('/astutus') """
    page_data = {
        'title': "Astutus",
        'show_links_section': True,
    }
    links = {
        "astutus/doc/index.html",
        "astutus/raspi",
    }
    return flask.render_template(
        'generic_rest_page.html',
        page_data=page_data,
        links=links)


def process_raspi_find_form(form):
    ipv4 = form.get("ipv4")
    logger.debug(f"ipv4: {ipv4}")
    mask = flask.request.form.get("mask")
    logger.debug(f"mask: {mask}")
    filter = form.getlist("filter")
    logger.debug(f"filter: {filter}")
    search_result = astutus.raspi.search_using_nmap(ipv4, mask, filter)
    return flask.render_template('raspi_find.html', search_result=search_result, filter=filter)


@app.route('/astutus/raspi', methods=['POST', 'GET'])
def handle_raspi():
    """ app.route('/astutus/raspi', methods=['POST', 'GET']) """
    if flask.request.method == 'GET':
        if flask.request.args.get('find') is not None:
            return flask.render_template('raspi_find.html', search_result=None, filter=['Raspberry'])
        items = astutus.db.RaspberryPi.query.all()
        page_data = {
            'title': "Astutus/Raspberry Pi's",
            'show_links_section': True,
            "show_post_section": True,
        }
        links = [f"raspi/{item.id}" for item in items]
        links.append('raspi?find=nmap')
        return flask.render_template(
            'generic_rest_page.html',
            page_data=page_data,
            links=links)
    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "seach_using_nmap":
            return process_raspi_find_form(form)
        if form.get("action") == "create":
            raspi_ipv4 = form.get("raspi_ipv4")
            raspi_mac_addr = form.get("raspi_mac_addr")
            rpi = astutus.db.RaspberryPi(ipv4=raspi_ipv4, mac_addr=raspi_mac_addr)
            db.session.add(rpi)
            db.session.commit()
            logger.debug(f"rpi: {rpi}")
            return flask.redirect(flask.url_for('handle_raspi_item', id=rpi.id))
        return "Case not handled", HTTPStatus.NOT_IMPLEMENTED


@app.route('/astutus/raspi/<int:id>', methods=['POST', 'GET', 'DELETE'])
def handle_raspi_item(id):
    """ app.route('/astutus/raspi/<int:id>', methods=['POST', 'GET', 'DELETE']) """
    if flask.request.method == 'POST':
        return "Got here"
    if flask.request.method == 'DELETE':
        item = astutus.db.RaspberryPi.query.get(id)
        db.session.delete(item)
        db.session.commit()
        data = {
            "redirect_url": "/astutus/raspi"
        }
        return data, HTTPStatus.ACCEPTED
    if flask.request.method == 'GET':
        item = astutus.db.RaspberryPi.query.get(id)
        page_data = {
            'title': "Raspberry Pi's",
            'show_links_section': False,
            "show_post_section": True,
            "show_delete_section": True,
            "show_raw_json_section": True,
        }
        return flask.render_template(
            'generic_rest_page.html',
            page_data=page_data,
            data=item.as_json(),
            links=None)


@app.route('/astutus/raspi/<int:id>/ifconfig', methods=['GET'])
def handle_raspi_item_ifconfig(id):
    """" app.route('/astutus/raspi/<int:id>/ifconfig', methods=['GET']) """
    item = astutus.db.RaspberryPi.query.get(id)
    raspi = astutus.raspi.RaspberryPi(item)
    ifconfig = raspi.get_ifconfig()
    page_data = {
        'title': "Raspberry Pi - ifconfig",
        'show_links_section': False,
        "show_post_section": False,
        "show_delete_section": False,
        "show_raw_json_section": True,
    }
    return flask.render_template(
        'generic_rest_page.html',
        page_data=page_data,
        data=ifconfig,
        links=None)


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
