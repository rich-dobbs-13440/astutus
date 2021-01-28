#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"

mark_sub_section "Install Astutus Package In a Virtual Environment"
cd ${this_dir}/dist
unset PYTHONPATH
python3 -m venv dist_venv
source dist_venv/bin/activate
# pip  install --upgrade pip wheel setuptools
pip install astutus-*-py3-none-any.whl
# Hardcode python version for now.
python_lib_dir="python3.8"
wheels_destination="${this_dir}/dist/dist_venv/lib/${python_lib_dir}/site-packages/astutus/wheels/"

mark_sub_section "Self-publish Package Wheels"
source "${this_dir}/fetch_wheels.sh"
cp "${this_dir}"/dist/*.whl "${wheels_destination}"
cp "${this_dir}"/wheels/none-any/*.whl "${wheels_destination}"
cp "${this_dir}"/wheels/none-any/*.tar.gz "${wheels_destination}"
cp "${this_dir}"/wheels/linux_armv7l/*.whl "${wheels_destination}"
cp "${this_dir}"/wheels/manylinux1_x86_64/*.whl "${wheels_destination}"

mark_sub_section "Launch Flask Application"

python3 -m astutus.web.flask_app
