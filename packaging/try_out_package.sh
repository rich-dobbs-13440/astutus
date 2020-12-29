#!/usr/bin/env bash

# Should be sourced!

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"

deactivate && true

cd ${this_dir}/dist
unset PYTHONPATH
python3 -m venv dist_venv
source dist_venv/bin/activate
pip install astutus-*-py3-none-any.whl

set +e
set +x