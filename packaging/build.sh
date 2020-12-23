#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"

mark_section "Start Building"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )



cp "${this_dir}/astutus_customization.sh" "${REPOPATH}/venv/bin/"

mark_sub_section "Activate Virtual Environment"
source "${REPOPATH}/venv/bin/activate"

cd "${REPOPATH}/docs"
make html

cd "${REPOPATH}"

mark_sub_section "Build Documentation"
rm -rf src/astutus/web/static/_docs

cp -r docs/_build/html src/astutus/web/static/_docs


mark_sub_section "Build Package"
python -m pep517.build packaging/

mark_sub_section "View Package Contents"
rm -rf packaging/dist/content/ && true
unzip  -d packaging/dist/content/ packaging/dist/astutus-*.whl

mark_sub_section "Self-publish Package Wheel"
rm  "${REPOPATH}"/src/astutus/wheels/*.whl && true

cp "${this_dir}"/dist/*.whl "${REPOPATH}/src/astutus/wheels/"
