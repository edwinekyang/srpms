#!/usr/bin/env bash

set -e

if [ "$DEBUG" == "True" ] || [ "$TEST" == "True" ]; then
    # Setting host.docker.internal, in case we need to access services bind to local interface
    DOCKER_HOST="$(getent hosts host.docker.internal | cut -d' ' -f1)"
    if [ $DOCKER_HOST ]; then
        echo "Docker Host: $DOCKER_HOST (host.docker.internal)"
    else
        DOCKER_HOST=$(ip -4 route show default | cut -d' ' -f3)
        echo -e "$DOCKER_HOST\thost.docker.internal" | tee -a /etc/hosts > /dev/null
        echo "Docker Host: $DOCKER_HOST (default gateway)"
    fi
fi

if [ "$DEBUG" == "False" ]; then
    echo "LDAP server point to $LDAP_ADDR"

    echo "### Perform deploy check ..."
    python manage.py check --deploy

    # Collect static files in production, these files are serve by gunicorn during development.
    # Consider moving this to Dockerfile if it takes too long to collect.
    echo "### Collect static files ..."
    python manage.py collectstatic --noinput

    echo "### Perform database migraitons ..."
    python manage.py migrate

    exec gunicorn --bind :8000 srpms.wsgi:application
elif [ "$DEBUG" == "True" ]; then
    IP_PREFIX=$(awk -v addr="$(wget -qO - ipinfo.io/ip)" 'BEGIN{split(addr,ip,"."); print ip[1] "." ip[2]}')

    if [ "$IP_PREFIX" == "150.203" ]; then
        # If inside ANU Network, directly point to ANU LDAP server
        export LDAP_ADDR="ldap://ldap.anu.edu.au"
    fi

    echo "LDAP server point to $LDAP_ADDR"

    exec gunicorn --reload --bind :8000 srpms.wsgi:application
else
    echo "Unknown setting '$DEBUG' for DJANGO_DEBUG_MODE"
    exit 1
fi


