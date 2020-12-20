set -x
export FLASK_APP="$( cd ../..; find -name "flask_app.py" -exec realpath {} \; )"
export FLASK_ENV=development