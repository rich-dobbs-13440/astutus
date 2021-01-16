#!/usr/bin/env bash

# Makes the virtual venv, and modifies it so that
# environment variables for this project can be set.


set -x
set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export REPOPATH=$( cd ${this_dir}/.. ; pwd )

deactivate || true

cd "${REPOPATH}"

rm -rf venv/
python3 -m venv venv

cp "${this_dir}/astutus_customization.sh" "venv/bin/"

# Modify the bash version of the activate script

printf "\nsource astutus_customization.sh\n" >> venv/bin/activate

source venv/bin/activate

pip install -r "${this_dir}/requirements.txt"
