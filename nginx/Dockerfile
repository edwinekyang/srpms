FROM nginx:1.17-alpine

COPY ./start.sh /start.sh
COPY ./conf.d /etc/nginx/conf.d

RUN chmod 700 /start.sh && \
    apk add --no-cache bash ca-certificates wget openssl && \
    update-ca-certificates

CMD ["/start.sh"]
