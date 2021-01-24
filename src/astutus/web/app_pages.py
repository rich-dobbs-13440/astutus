import logging

import flask
import flask.logging

logger = logging.getLogger(__name__)
app_page = flask.Blueprint('app_bp', __name__, template_folder='templates')


@app_page.route('/')
def handle_top():
    """ app_page.route('/') """
    return flask.redirect(flask.url_for("handle_astutus"))


@app_page.route('/astutus/app/dyn_index.html', methods=['GET'])
def handle_app_index_from_doc():
    return flask.redirect(flask.url_for("handle_astutus"))


@app_page.route('/astutus/app/index.html')
def handle_astutus():
    links_list = [
        '<li><p>Control the <a class="reference internal" href="/astutus/log">logging</a> in the web application.</p></li>'  # noqa
        '<li><p>Discover and work with <a class="reference internal" href="/astutus/app/raspi"><span class="doc">Raspberry Pi\'s</span> on your system</a></p></li>',  # noqa
        '<li><p>Understand the <a class="reference internal" href="/astutus/app/usb"><span class="doc">USB devices</span></a> on you system</p></li>',  # noqa
    ]
    links = "\n".join(links_list)
    return flask.render_template(
        'dyn_index.html',
        links=links)
