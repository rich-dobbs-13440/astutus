#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )

mark_section "Start Cleaning"

mark_sub_section "Package build"
rm -rf "${this_dir}/build"

mark_sub_section "Package dist"
rm -rf "${this_dir}/dist"

mark_sub_section "Package src"
rm -rf "${this_dir}/src"

mark_sub_section "Docs _build"
rm -rf "${REPOPATH}/docs/_build"
