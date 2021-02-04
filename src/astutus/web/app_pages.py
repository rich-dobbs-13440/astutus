import logging
from http import HTTPStatus

import flask
import flask.logging

logger = logging.getLogger(__name__)
app_page = flask.Blueprint('app_bp', __name__, template_folder='templates')


@app_page.route('/')
def handle_top():
    """ app_page.route('/') """
    return flask.redirect(flask.url_for("app_bp.handle_astutus"))


@app_page.route('/astutus/app/index.html')
def handle_astutus():
    return flask.render_template('app/styled_index.html')


@app_page.route('/astutus/internalerror/<path:path>', methods=['GET'])
def handle_internalerror(path):
    args = flask.request.args
    logger.error(f'Internal error from client:  {args}')
    return f"args: {args}", HTTPStatus.INTERNAL_SERVER_ERROR
