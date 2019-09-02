#!/usr/bin/env sh

pid=1

cleanup() {
    echo "Exiting ..."

    if [ $pid -ne 1 ]; then
        kill -SIGTERM "-$pid"
        wait "$pid"
    fi

    exit
}

set -e

if [ "$DEBUG" == "True" ]; then
    trap cleanup INT TERM
    npm install
    ng build --watch --output-path /dist/srpms-client &
    pid="${!}"
    wait "$pid"
else
    # Clean up and copy file to volume
    rm -rf /dist/*
    cp -r ./dist/* /dist/
    exit 0
fi
