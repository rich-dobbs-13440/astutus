#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"

cd ${this_dir}/dist
unset PYTHONPATH
python3 -m venv venv
source venv/bin/activate
pip install astutus-*-py3-none-any.whl
python3 -m astutus.web.flask_app
