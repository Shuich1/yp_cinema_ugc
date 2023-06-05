#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd src
if [ "$USE_GUNICORN" = "true" ]
then
echo "Starting with GUNICORN"
gunicorn $UVICORN_APP_NAME --workers $UVICORN_WORKERS --worker-class uvicorn.workers.UvicornWorker --bind $UVICORN_HOST:$UVICORN_PORT
else
echo "Starting without GUNICORN"
python main.py
fi