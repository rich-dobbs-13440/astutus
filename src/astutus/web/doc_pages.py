import logging
# from http import HTTPStatus
import os

import flask
import flask.logging

logger = logging.getLogger(__name__)
db = None
static_base = None
doc_page = flask.Blueprint('doc', __name__, template_folder='templates')


@doc_page.route('/astutus/_static/<path:path>')
def handle_underscore_static_path(path):
    """ doc_page.route('/astutus/doc/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', '_static', path)
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/source/<path:path>')
def handle_source_path(path):
    """ doc_page.route('/astutus/source/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'source', path)
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/doc/<path:path>')
def handle_doc_path(path):
    """ doc_page.route('/astutus/doc/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'doc', path)
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/index.html')
def handle_top_index():
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'index.html')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)
