#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )

cp "${this_dir}/astutus_customization.sh" "${REPOPATH}/venv/bin/"

source "${REPOPATH}/venv/bin/activate"

cd "${REPOPATH}/docs"
make html

cd "${REPOPATH}"

rm -rf src/astutus/web/static/_docs

cp -r docs/_build/html src/astutus/web/static/_docs
