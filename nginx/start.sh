#!/usr/bin/env bash
# Custom behavior on Nginx startup, i.e. configure self-signed certificate if certificate no found
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

pid=1

set -e

eval DOMAINS=$DOMAINS

mkdir -p "$CERTBOT_PATH"
mkdir -p "$LETS_ENC_PATH"

echo "### Checking TLS parameter files ..."
if [ ! -e "$LETS_ENC_PATH/options-ssl-nginx.conf" ] || [ ! -e "$LETS_ENC_PATH/ssl-dhparams.pem" ]; then
  echo "Not found, downloading recommended TLS parameters from certbot github ..."
  wget -qO- https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/tls_configs/options-ssl-nginx.conf > "$LETS_ENC_PATH/options-ssl-nginx.conf"
  wget -qO- https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem > "$LETS_ENC_PATH/ssl-dhparams.pem"
else
  echo "Found."
fi

echo "### Checking certficates ..."
if [ -e "$LETS_ENC_PATH/live/$DOMAINS/fullchain.pem" ] && [ -e "$LETS_ENC_PATH/live/$DOMAINS/privkey.pem" ]; then
  echo "Certificates already exist."
else
  echo "Couldn't find certificate, Creating dummy certificate for $DOMAINS ..."
  mkdir -p "$LETS_ENC_PATH/live/$DOMAINS"
  openssl req -x509 -nodes -newkey rsa:2048 -days 1\
    -keyout "$LETS_ENC_PATH/live/$DOMAINS/privkey.pem" \
    -out "$LETS_ENC_PATH/live/$DOMAINS/fullchain.pem" \
    -subj "/CN=localhost"
fi

echo "### Starting nginx ..."
exec nginx -g "daemon off;"
