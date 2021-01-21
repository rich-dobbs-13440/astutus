import logging
import os
# from http import HTTPStatus

# import astutus.log
import flask
import flask.logging

logger = logging.getLogger(__name__)
# db = None
# static_base = None
doc_page = flask.Blueprint('doc', __name__, template_folder='templates')


# @doc_page.route('/astutus/doc')
# def handle_doc():
#     """ @app.route('/astutus/doc') """
#     return flask.redirect(flask.url_for("handle_doc_top"))


@doc_page.route('/astutus/doc/<path:path>')
def handle_doc_path(path):
    logger.debug(f"app.root_path: {doc_page.root_path}")
    dir = os.path.dirname(path)
    basename = os.path.basename(path)
    directory = os.path.join(doc_page.root_path, 'static', '_docs', dir)
    print(f"directory: {directory}")
    return flask.send_from_directory(directory, basename)


# @doc_page.route('/astutus/doc/_static/<path:path>')
# def handle_underscore_static(path):
#     logger.debug(f"app.root_path: {doc_page.root_path}")
#     dir = os.path.dirname(path)
#     basename = os.path.basename(path)
#     directory = os.path.join(doc_page.root_path, 'static', '_docs', '_static', dir)
#     print(f"directory: {directory}")
#     return flask.send_from_directory(directory, basename)


# @doc_page.route('/dyn_pages/astustus/index.html')
# def handle_ref_from_doc_to_dyn_pages():
#     logger.debug("hit /dyn_pages/astustus/index.html")
#     return flask.redirect("/astutus/index.html")


# @doc_page.route('/dyn_pages/astustus/<path:path>')
# def handle_doc_reference_to_dyn_page(path):
#     logger.debug(f"path: {path}")
#     return flask.redirect("/astutus/" + path)


# @doc_page.route('/astutus/doc/dyn_pages/<path:path>')
# def handle_doc_reference_to_dyn_page_1(path):
#     if path == 'dyn_index.html':
#         return flask.redirect(flask.url_for('handle_app_index'))
#     return flask.redirect("/" + path)


# @doc_page.route('/astutus/doc/<path:path>')
# def handle_doc_path(path):
#     """ app.route('/astutus/doc/<path:path>') """
#     print(f"path: {path}")
#     # print(f"filename: {filename}")
#     logger.debug(f"app.root_path: {app.root_path}")
#     real_path = os.path.join(app.root_path, 'static', '_docs', 'astutus', 'doc', path)
#     print(f"real_directory: {real_path}")
#     return flask.send_file(real_path)
