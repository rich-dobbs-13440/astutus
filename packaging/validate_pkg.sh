#!/usr/bin/env bash

cd astutus/packaging/dist
python3 -m venv venv
source venv/bin/activate
pip install astutus-*-py3-none-any.whl
python3 -m astutus.web.flask_app
