# Certbot is a tool for obtaining free HTTPS certificate from Let's Encrypt.
# This certbot image also add docker-compose support, so that it can tell
# Nginx to reload after a new certificate has been obtained.
#
# Refer to https://certbot.eff.org/docs/contributing.html#running-the-client-with-docker for
# certbot's official documentation about how certbot works
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

FROM certbot/certbot

ENTRYPOINT ["/bin/bash"]

# Copy docker and docker-compose binary
COPY --from=docker/compose:1.24.1 /usr/local/bin/* /usr/local/bin/

ENV GLIBC=2.28-r0

# Command obtain from "docker history --no-trunc docker/compose:1.24.1"
RUN apk update && \
    apk add --no-cache bash openssl ca-certificates curl libgcc && \
    curl -fsSL -o /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
    curl -fsSL -o glibc-$GLIBC.apk https://github.com/sgerrand/alpine-pkg-glibc/releases/download/$GLIBC/glibc-$GLIBC.apk && \
    apk add --no-cache glibc-$GLIBC.apk && \
    ln -s /lib/libz.so.1 /usr/glibc-compat/lib/ && \
    ln -s /lib/libc.musl-x86_64.so.1 /usr/glibc-compat/lib && \
    ln -s /usr/lib/libgcc_s.so.1 /usr/glibc-compat/lib && \
    rm /etc/apk/keys/sgerrand.rsa.pub glibc-$GLIBC.apk && \
    apk del curl

WORKDIR /srpms
COPY . .
RUN chmod u+x ./certbot/start.sh

CMD ["./certbot/start.sh"]
