import logging
from http import HTTPStatus

import astutus.log
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.addHandler(flask.logging.default_handler)

log_page = flask.Blueprint('log', __name__, template_folder='templates')

static_base = None

wy_menu_vertical_list = [
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc">Welcome</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus">Browser Astutus</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb">Browser USB Capabilities</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb/device">Browser USB Devices</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb/alias">Browser USB Device Aliases</a></li>',  # noqa
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc/command_line">Command Line Astutus</a></li>',  # noqa
]
wy_menu_vertical = "\n".join(wy_menu_vertical_list)


@log_page.route('/astutus/log', methods=['POST', 'GET'])
def handle_log():
    """ log_page.route('/astutus/log', methods=['POST', 'GET']) """
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/log</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        loggers = astutus.log.get_loggers()
        return flask.render_template(
            'log/dyn_log.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            loggers=loggers)
    if flask.request.method == 'POST':
        # loglevel = getattr(logging, args.loglevel)
        return "POST method not implemented", HTTPStatus.NOT_IMPLEMENTED
