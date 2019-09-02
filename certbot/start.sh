#!/usr/bin/env bash

pid=1

cleanup() {
    echo "Exiting ..."
    
    if [ $pid -ne 1 ]; then
        kill -SIGTERM "$pid"
        wait "$pid"
    fi
    
    exit
}

trap cleanup INT TERM

set -e

# Convert the array to actually bash array
eval DOMAINS=$DOMAINS

if [ $DRY_RUN != 0 ]; then
    staging_arg="--dry-run"
    purge_cmd="find"
else
    purge_cmd="rm -vrf"
fi

echo "### Check certificate for $DOMAINS ..."

while [ ! -e "$LETS_ENC_PATH/live/$DOMAINS/fullchain.pem" ]; do
    echo "Can't find certificate, wait for 10s ..."
    sleep 10s
done

CERT_CN_RAW=$(openssl x509 -noout -subject -in "$LETS_ENC_PATH/live/$DOMAINS/fullchain.pem")
CERT_CN=$(awk -v cn_raw="$CERT_CN_RAW" 'BEGIN{split(cn_raw,info," "); print info[3]}')

if [ "$CERT_CN" == "localhost" ]; then
    echo "Dummy certificate detected, purging configurations ..."

    set +e
    $purge_cmd "$LETS_ENC_PATH/live/$DOMAINS"
    $purge_cmd "$LETS_ENC_PATH/archive/$DOMAINS"
    $purge_cmd "$LETS_ENC_PATH/renewal/$DOMAINS.conf"
    set -e

    echo "Requesting Let's Encrypt certificate for $DOMAINS ..."

    #Join $domains to -d args
    domain_args=""
    for domain in "${DOMAINS[@]}"; do
        domain_args="$domain_args -d $domain"
    done

    # Select appropriate email arg
    case "$CERT_EMAIL" in
        "") email_arg="--register-unsafely-without-email" ;;
        *) email_arg="--email $CERT_EMAIL" ;;
    esac

    # PLEASE NOTE THAT THE RATE LIMIT OF RENEWAL IS 5 PER WEEK
    # Check https://letsencrypt.org/docs/rate-limits/ for more details
    certbot certonly -n --webroot -w /var/www/certbot \
        $staging_arg \
        $email_arg \
        $domain_args \
        --rsa-key-size $RSA_KEY_SIZE \
        --agree-tos \
        --force-renewal
else
    echo "No dummy certificate detected."
fi

echo "### Start renew daemon ..."
while :; do
    certbot renew $staging_arg --deploy-hook "\
        echo \"Certificates renewed, reloading nginx ...\" && \
        docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload"
    sleep 12h
done &
pid="${!}"
wait $pid
