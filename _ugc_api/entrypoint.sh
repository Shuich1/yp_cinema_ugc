#!/bin/sh

set -e

python /opt/app/utils/wait_for_services.py
exec "${@}"
