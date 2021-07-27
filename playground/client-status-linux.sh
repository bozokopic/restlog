#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $PYTHON -m restlog.clients.status.linux \
    --source client1 \
    http://127.0.0.1:23233
