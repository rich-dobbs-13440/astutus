set -x
# export PYTHONPATH="$( cd ../../src ; pwd )"
pwd
export PYTHONPATH="$( cd src ; pwd )"
export FLASK_APP="$( cd ../..; find -name "flask_app.py" -exec realpath {} \; )"
export FLASK_ENV=development

set +x