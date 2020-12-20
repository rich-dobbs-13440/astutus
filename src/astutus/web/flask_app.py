import flask

app = flask.Flask('astutus')


@app.route('/')
def handle_top():
    return "Hi there."


@app.route('/astutus')
def handle_astutus():
    return "Got to astutus"


if __name__ == '__main__':
    # run_simple('localhost', 5000, app,
    #            use_reloader=True, use_debugger=True, use_evalex=True)

    app.run()