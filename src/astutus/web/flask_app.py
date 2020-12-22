#!/usr/bin/env python3
import json
import os
from http import HTTPStatus
import logging

import astutus.raspi
import astutus.web.flask_app
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = flask.Flask('astutus.web.flask_app', template_folder='templates')

library_handler = logging.StreamHandler(flask.logging.wsgi_errors_stream)
library_handler.setFormatter(
    # Set format suitable for clicking in terminal in Visual Studio Code (Ctrl or Cmd Click)
    logging.Formatter("[%(asctime)s] %(levelname)s File \"%(pathname)s:%(lineno)d\" %(message)s")
)
flask.logging.default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s File \"%(pathname)s:%(lineno)d\" %(message)s")
)
# app.logger.addHandler(flask.logging.default_handler)
astutus.raspi.find.logger.addHandler(library_handler)
logger.addHandler(library_handler)


@app.template_filter('tojson_pretty')
def tojson_pretty(json_text):
    """Pretty Print Json"""
    parsed_json = json.loads(json_text)
    return json.dumps(parsed_json, indent=4, sort_keys=True)


@app.route('/')
def handle_top():
    return "Hi there."


@app.route('/astutus')
def handle_astutus():
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


def handle_rasp_find(form):
    ipv4 = form.get("ipv4")
    logger.debug(f"ipv4: {ipv4}")
    mask = flask.request.form.get("mask")
    logger.debug(f"mask: {mask}")
    filter = []
    raspi_filter = form.get("raspi")
    logger.debug(f"raspi_filter: {raspi_filter}")
    if raspi_filter is not None:
        filter.append(raspi_filter)
    vnc_filter = form.get("vnc")
    logger.debug(f"vnc_filter: {vnc_filter}")
    if vnc_filter is not None:
        filter.append(vnc_filter)
    ssh_filter = form.get("ssh")
    logger.debug(f"ssh_filter: {ssh_filter}")
    if ssh_filter is not None:
        filter.append(ssh_filter)
    search_result = astutus.raspi.search_using_nmap(ipv4, mask, filter)
    return flask.render_template('raspi_find.html', search_result=search_result)



@app.route('/astutus/raspi', methods=['POST', 'GET'])
def handle_raspi():
    if flask.request.method == 'GET':
        if flask.request.args.get('find') is not None:
            return flask.render_template('raspi_find.html', search_result=None)
        page_data = {
            'title': "Astutus/Raspberry Pi's",
            'show_links_section': True,
            "show_post_section": True,
        }
        links = {
            "astutus/raspi/1",
        }
        return flask.render_template(
            'generic_rest_page.html',
            page_data=page_data,
            links=links)
    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "seach_using_nmap":
            return handle_rasp_find(form)
        return "Should create and show newly created item", HTTPStatus.NOT_IMPLEMENTED


@app.route('/astutus/doc')
def handle_doc():
    return flask.redirect(flask.url_for("doc_top"))


@app.route('/astutus/doc/index.html')
def doc_top():
    directory = os.path.join(app.root_path, 'web', 'static', '_docs')
    print(f"directory: {directory}")
    return flask.send_from_directory(directory, 'index.html')


@app.route('/astutus/doc/<path:path>')
def doc(path):
    print(f"path: {path}")
    # print(f"filename: {filename}")
    real_path = os.path.join(app.root_path, 'web', 'static', '_docs', path)
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
