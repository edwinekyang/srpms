FROM node:10-alpine

ARG DEBUG

# Arbitrary location choice
RUN mkdir -p /app/srpms-client
WORKDIR /app/srpms-client

# Install angular
RUN npm install -g @angular/cli@8 && \
    npm cache clean --force && \
    rm -rf ~/.npm && \
    apk add --no-cache bash

COPY ./* ./
RUN if [ "$DEBUG" == "True" ]; then \
        echo "Debug, skip build"; \
    else \
        npm install && \
        ng build --prod && \
        rm -rf node_modules; \
    fi

CMD ["./start.sh"]
