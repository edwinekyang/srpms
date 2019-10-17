#!/usr/bin/env bash
# Angular startup script, define start up behavior according to the environment.
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

pid=1

cleanup() {
    echo "Exiting ..."

    if [ $pid -ne 1 ]; then
        kill -SIGTERM "$pid"
        trap 'rc=$?; if [ $rc == "143" ]; then exit 0; else exit $rc; fi' EXIT
        wait "$pid"
    fi 
}

set -e

if [ "$DEBUG" == "True" ]; then
    trap cleanup INT TERM
    npm install
    ng build --watch --output-path /dist/srpms-client &
    pid="${!}"
    wait "$pid"
else
    # Clean up and copy file to Nginx
    rm -rf /dist/*
    cp -r ./dist/* /dist/
    exit 0
fi
