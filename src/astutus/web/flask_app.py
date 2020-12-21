#!/usr/bin/env python3
# from http import HTTPStatus
import os
import json

import astutus.web.flask_app
import flask

app = flask.Flask('astutus', template_folder='./web/templates')


@app.template_filter('tojson_pretty')
def caps(json_text):
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
    # real_path = os.path.join(real_directory, filename)
    # print(f"real_path: {real_path}")
    # return "Working on it", HTTPStatus.NOT_IMPLEMENTED
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
