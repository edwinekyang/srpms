#!/usr/bin/env sh

set -e

if [ "$DEBUG" == "True" ]; then
    npm install
    ng build --watch
else
    # Clean up and copy file to volume
    rm -rf /dist/*
    cp -r ./dist/* /dist/
    exit 0
fi
