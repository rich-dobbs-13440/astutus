set -x
# export PYTHONPATH="$( cd ../../src ; pwd )"
pwd
export PYTHONPATH="$( cd src ; pwd )"
export FLASK_APP="$( cd ../..; find -name "flask_app.py" -exec realpath {} \; )"
export FLASK_ENV=development
export ASTUTUS_DB_URL="sqlite:////tmp/astutus.db"

set +x