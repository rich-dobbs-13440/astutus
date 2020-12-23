#!/usr/bin/env bash

set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${this_dir}/utilities.sh"

mark_section "Start Fetching Wheels"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )

cd "${REPOPATH}"

mkdir -p packaging/wheels/none-any
mkdir -p packaging/wheels/linux_armv7l
mkdir -p packaging/wheels/manylinux1_x86_64

cd "${REPOPATH}/packaging/wheels/none-any"

pip3 download -r ../../requirements.txt
cd "${REPOPATH}/packaging/wheels"
mv none-any/*.manylinux1_x86_64.whl manylinux1_x86_64 && true

# TODO: Handle MarkupSafe and SQLAlchemy which are *linux_armv7l.whl
#     Use a docker instance to get platform independence? 
#     Remote to an available PI?
#     Do it efficiently as part of adoption?  * This seems like the winner

print_success "All steps done"

mark_end_section "Building and Configuring Package"