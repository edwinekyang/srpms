# Angular container, this container would serve the angular front-end on development mode,
# run tests on test mode, or compile the front-end code in deployment mode.
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

FROM node:10-alpine

ARG DEBUG
ARG TEST

# Arbitrary location choice
RUN mkdir -p /app/srpms-client
WORKDIR /app/srpms-client

# Install angular
RUN npm install -g @angular/cli@8 && \
    npm cache clean --force && \
    rm -rf ~/.npm && \
    apk add --no-cache bash

# In order to run Karma we need chrome headless
RUN if [ "$TEST" == "True" ]; then \
        apk add --no-cache nodejs nodejs-npm bash chromium nss chromium-chromedriver; \
    fi

COPY . .
RUN if [ "$DEBUG" == "True" ]; then \
        echo "Debug, skip build"; \
    else \
        npm install && \
        ng build --prod; \
    fi && \
    if [ "$TEST" != "True" ]; then \
        rm -rf node_modules; \
    fi

# Note that these two variable only valid when TEST=True
ENV CHROME_BIN='/usr/bin/chromium-browser'
ENV CHROME_DRIVER='/usr/bin/chromedriver'

CMD ["./start.sh"]
