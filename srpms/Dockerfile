# Build docker image for Django server
# TODO: WeasyPrint take significant amount of space for this image, find some way to optimize size
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

FROM python:3.7-alpine

ARG DEBUG

# arbitrary location choice
RUN mkdir -p /djangoproj/srpms
WORKDIR /djangoproj/srpms

# install dependencies
RUN apk add --no-cache libldap libsasl postgresql-libs postgresql-client bash \
                       cairo-dev pango-dev gdk-pixbuf
# install fonts needed for printing pdf contract
RUN apk add --no-cache msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f
RUN apk add --no-cache --virtual .build-deps \
                       postgresql-dev \
                       gcc \
                       musl-dev \
                       openldap-dev \
                       jpeg-dev \
                       zlib-dev \
                       libffi-dev \
    && pip install psycopg2==2.7.* \
                   gunicorn==19.9.* \
                   django==2.2.* \
                   djangorestframework==3.10.* \
                   django-auth-ldap==2.0.* \
                   django-filter==2.2.* \
                   markdown==3.1.* \
                   djangorestframework_simplejwt==4.3.* \
                   django-cors-headers==3.1.* \
                   drf-extensions==0.5.* \
                   ipython==7.7.* \
                   pylint_django==2.0.* \
                   coverage==4.5.* \
                   WeasyPrint==50.* \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

RUN if [ "$DEBUG" == "True" ]; then \
        pip install django-debug-toolbar; \
    fi

# copy our project code
COPY . .

# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
CMD ["./start.sh"]
