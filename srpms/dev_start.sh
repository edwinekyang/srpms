#!/usr/bin/env sh

set -e

IP_PREFIX=$(awk -v addr="$(wget -qO - ipinfo.io/ip)" 'BEGIN{split(addr,ip,"."); print ip[1] "." ip[2]}')

if [ "$IP_PREFIX" == "150.203" ]; then
    # If inside ANU Network, directly point to ANU LDAP server
    export LDAP_ADDR="ldap://ldap.anu.edu.au"
else
    # Setting host.docker.internal to access ANU LDAP bind to local interface
    DOCKER_HOST="$(getent hosts host.docker.internal | cut -d' ' -f1)"
    if [ $DOCKER_HOST ]; then
        echo "Docker Host: $DOCKER_HOST (host.docker.internal)"
    else
        DOCKER_HOST=$(ip -4 route show default | cut -d' ' -f3)
        echo -e "$DOCKER_HOST\thost.docker.internal" | tee -a /etc/hosts > /dev/null
        echo "Docker Host: $DOCKER_HOST (default gateway)"
    fi
fi

echo "LDAP server point to $LDAP_ADDR"

gunicorn --reload --bind :8000 srpms.wsgi:application
