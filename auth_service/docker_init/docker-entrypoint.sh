# Wait start DB server
echo "Wait start DB server"
docker_init/wait-for-it.sh $DB_HOST:$DB_PORT -t $WAIT_TIMEOUT

# Wait cache DB
echo "Wait start cache DB"
docker_init/wait-for-it.sh $REDIS_HOST:$REDIS_PORT -t $WAIT_TIMEOUT

# change folder
cd src

flask db upgrade

# Start server
echo "Starting server"
gunicorn --worker-class gevent \
  --workers $UVICORN_WORKERS \
  --bind $APP_HOST:$APP_PORT \
  wsgi_app:app