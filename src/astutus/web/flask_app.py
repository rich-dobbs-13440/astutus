import os
# from http import HTTPStatus

import flask

app = flask.Flask('astutus')


@app.route('/')
def handle_top():
    return "Hi there."


@app.route('/astutus')
def handle_astutus():
    return "Got to astutus"


# @app.route('/astutus/doc')
# def handle_docs():
#     return "Got to doc"

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


if __name__ == '__main__':
    # run_simple('localhost', 5000, app,
    #            use_reloader=True, use_debugger=True, use_evalex=True)

    app.run()
