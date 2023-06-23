#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker-compose logs -f ugc-tests
docker-compose down --remove-orphans --volumes
