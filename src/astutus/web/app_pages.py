import logging

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
    return flask.render_template('app/dyn_index.html')
