#!/usr/bin/env bash

set -e
set +x

# This script would be run inside the CI container, make sure you have
# bash installed there.

COMPOSE_CMD=$1

if [ "$COMPOSE_CMD" == "" ]; then
    echo "Please specify compose command, exit with error ..."
    exit 1
else
    echo "COMPOSE_CMD: $COMPOSE_CMD"
fi

# Check how many non-zero code do we have
STATUS="$($COMPOSE_CMD ps -q | xargs docker inspect -f '{{ .State.ExitCode }}' | grep -v '^0' | wc -l | tr -d ' ')"

# Print logs on non-zero exit code and exit
if [ "$STATUS" != "0" ]; then
    $COMPOSE_CMD logs
    $COMPOSE_CMD ps

    exit "$STATUS"
else
    $COMPOSE_CMD ps
fi
