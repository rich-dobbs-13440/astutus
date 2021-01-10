set -x
pwd
export PYTHONPATH="$( cd src ; pwd )"
export FLASK_APP="astutus.web.flask_app:app"
export FLASK_ENV=development
# Uncomment the following line to replace database
# with every build.
# export ASTUTUS_DB_URL="sqlite:///astutus.db"

set +x