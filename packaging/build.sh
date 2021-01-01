#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )

source "${this_dir}/clean.sh"

mark_section "Start Building"

if [ ! -d "${REPOPATH}/venv/bin/" ]; then
    source "${this_dir}/make_venv.sh"
fi
cp "${this_dir}/astutus_customization.sh" "${REPOPATH}/venv/bin/"


mark_sub_section "Activate Virtual Environment"
source "${REPOPATH}/venv/bin/activate"


mark_sub_section "Build Documentation"
cd "${REPOPATH}/docs"
make html
cd "${REPOPATH}"
rm -rf src/astutus/web/static/_docs
cp -r docs/_build/html src/astutus/web/static/_docs
cd "$this_dir"
./prepare_jinja2_templates_from_sphinx_templates.py

mark_sub_section "Build Package"
cd "${REPOPATH}"
python -m pep517.build packaging/


mark_sub_section "View Package Contents"
rm -rf packaging/dist/content/ && true
unzip  -d packaging/dist/content/ packaging/dist/astutus-*.whl


mark_sub_section "Self-publish Package Wheel"
source "${this_dir}/fetch_wheels.sh"
rm  "${REPOPATH}"/src/astutus/wheels/*.whl && true
mkdir -p "${REPOPATH}/src/astutus/wheels/"
cp "${this_dir}"/dist/*.whl "${REPOPATH}/src/astutus/wheels/"
cp "${this_dir}"/wheels/none-any/*.whl "${REPOPATH}/src/astutus/wheels/"

print_success "All steps done"

mark_end_section "End Building and Configuring Package"
