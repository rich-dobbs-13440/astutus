import logging
# from http import HTTPStatus
import os

import flask
import flask.logging

logger = logging.getLogger(__name__)
db = None
doc_page = flask.Blueprint('doc', __name__, template_folder='templates')

# TODO: Rename to something like Sphinx pages.


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
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'doc', path)
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/index.html')
def handle_top_index():
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'index.html')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/search.html')
def handle_search():
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'search.html')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/searchindex.js')
def handle_searchindex_js():
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'searchindex.js')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/genindex.html')
def handle_genindex():
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'genindex.html')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)


@doc_page.route('/astutus/py-modindex.html')
def handle_modindex():
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', 'py-modindex.html')
    logger.debug(f"real_path: {real_path}")
    return flask.send_file(real_path)
