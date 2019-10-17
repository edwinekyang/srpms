# Custom Nginx docker image to load configurations and custom startup behaviors
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

FROM nginx:1.17-alpine

# Note that when running inside CI container, mapping container's filesystem to another
# container is very dangerous and might have unexpected system
COPY ./start.sh /start.sh
COPY ./conf.d /etc/nginx/conf.d

RUN chmod 700 /start.sh && \
    apk add --no-cache bash ca-certificates wget openssl && \
    update-ca-certificates

CMD ["/start.sh"]
