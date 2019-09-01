FROM certbot/certbot

ENTRYPOINT ["/bin/sh"]

# Copy docker and docker-compose binary
COPY --from=docker/compose:1.24.1 /usr/local/bin/* /usr/local/bin/

ENV GLIBC=2.28-r0

# Command obtain from "docker history --no-trunc docker/compose:1.24.1"
RUN apk update && \
    apk add --no-cache openssl ca-certificates curl libgcc && \
    curl -fsSL -o /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
    curl -fsSL -o glibc-$GLIBC.apk https://github.com/sgerrand/alpine-pkg-glibc/releases/download/$GLIBC/glibc-$GLIBC.apk && \
    apk add --no-cache glibc-$GLIBC.apk && \
    ln -s /lib/libz.so.1 /usr/glibc-compat/lib/ && \
    ln -s /lib/libc.musl-x86_64.so.1 /usr/glibc-compat/lib && \
    ln -s /usr/lib/libgcc_s.so.1 /usr/glibc-compat/lib && \
    rm /etc/apk/keys/sgerrand.rsa.pub glibc-$GLIBC.apk && \
    apk del curl

WORKDIR /srpms
COPY ./certbot_start.sh /certbot_start.sh
RUN chmod u+x ./certbot_start.sh

CMD ["/certbot_start.sh"]
