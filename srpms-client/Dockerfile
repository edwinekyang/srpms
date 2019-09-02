FROM node:10-alpine

# Arbitrary location choice
RUN mkdir -p /app/srpms-client
WORKDIR /app/srpms-client

# Install
RUN npm install -g @angular/cli@8 && \
    npm install --save @angular/material @angular/cdk @angular/animations && \
    npm cache clean --force && \
    rm -rf ~/.npm
