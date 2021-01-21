import logging
from http import HTTPStatus

import astutus.log
import flask
import flask.logging

logger = logging.getLogger(__name__)
db = None
static_base = None
log_page = flask.Blueprint('log', __name__, template_folder='templates')


@log_page.route('/astutus/app/log/dyn_log.html', methods=['GET'])
def handle_log_from_doc():
    return flask.redirect(flask.url_for("log.handle_log"))


@log_page.route('/astutus/app/log/index.html', methods=['GET'])
def handle_log():
    """ log_page.route('/astutus/log', methods=[GET']) """
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
            loggers=loggers)
    if flask.request.method == 'POST':
        # loglevel = getattr(logging, args.loglevel)
        return "POST method not implemented", HTTPStatus.NOT_IMPLEMENTED


@log_page.route('/astutus/log/<logger_name>', methods=['PATCH'])
def handle_log_item(logger_name):
    """ log_page.route('/astutus/log/<logger_name>', methods=['PATCH']) """
    if flask.request.method == 'PATCH':
        logger.debug(f"logger_name: {logger_name}")
        request_data = flask.request.get_json(force=True)
        level = int(request_data.get('level'))
        logger.debug(f"level: {level}")
        astutus.log.set_level(logger_name, level)
        item = astutus.db.Logger.query.get(logger_name)
        if item is None:
            item = astutus.db.Logger(name=logger_name, level=level)
            db.session.add(item)
        else:
            item.level = level
        db.session.commit()
        items = astutus.db.Logger.query.all()
        logger.debug(f"logger items: {items}")
        return f"PATCH method - logger: {logger_name} level: {level}", HTTPStatus.OK
