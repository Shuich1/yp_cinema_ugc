#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker logs -f ugc-tests
exitcode="$(docker inspect ugc-tests --format={{.State.ExitCode}})"
docker-compose down --remove-orphans --volumes
exit "$exitcode"
