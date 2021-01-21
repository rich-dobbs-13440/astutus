import logging
# from http import HTTPStatus
import os

import flask
import flask.logging

logger = logging.getLogger(__name__)
db = None
static_base = None
doc_page = flask.Blueprint('doc', __name__, template_folder='templates')


# @doc_page.route('/astutus/doc/dyn_pages/<path:path>')
# def handle_doc_reference_to_dyn_page(path):
#     if path == 'dyn_index.html':
#         return flask.redirect(flask.url_for('handle_astutus'))
#     return path, HTTPStatus.NOT_IMPLEMENTED

@doc_page.route('/astutus/_static/<path:path>')
def handle_underscore_static_path(path):
    """ doc_page.route('/astutus/doc/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {doc_page.root_path}")
    real_path = os.path.join(doc_page.root_path, 'html', '_static', path)
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

# @doc_page.route('/astutus/doc')
# def handle_doc():
#     """ @app.route('/astutus/doc') """
#     return flask.redirect(flask.url_for("handle_doc_top"))


# @doc_page.route('/astutus/doc/index.html')
# def handle_doc_top():
#     """ app.route('/astutus/doc/index.html') """
#     logger.debug(f"app.root_path: {app.root_path}")
#     directory = os.path.join(app.root_path, 'static', '_docs')
#     print(f"directory: {directory}")
#     return flask.send_from_directory(directory, 'index.html')