#!/usr/bin/env sh

cleanup() {
    echo "Exiting ..."
    exit
}

trap cleanup INT TERM

set -e

if [ "$DEBUG" == "True" ]; then
    npm install
    ng build --watch --output-path /dist/srpms-client
else
    # Clean up and copy file to volume
    rm -rf /dist/*
    cp -r ./dist/* /dist/
    exit 0
fi
