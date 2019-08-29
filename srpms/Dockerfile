# start from an official image
FROM python:3.7-alpine

# arbitrary location choice
RUN mkdir -p /djangoproj/srpms
WORKDIR /djangoproj/srpms

# install dependencies
RUN apk add --no-cache libldap libsasl postgresql-libs
RUN apk add --no-cache --virtual .build-deps \
                       postgresql-dev \
                       gcc \
                       musl-dev \
                       openldap-dev \
    && pip install psycopg2==2.7 \
                   gunicorn==19.9 \
                   django==2.2 \
                   djangorestframework==3.10 \
                   django-auth-ldap==2.0 \
                   django-filter==2.2 \
                   markdown==3.1 \
                   ipython \
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

# copy our project code
COPY . /djangoproj/srpms/

# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
CMD ["gunicorn", "--bind", ":8000", "srpms.wsgi:application"]