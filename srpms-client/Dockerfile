FROM node:10-alpine

# Arbitrary location choice
RUN mkdir -p /app/srpms-client
WORKDIR /app/srpms-client

# Install
# TODO: Specify the angular version
RUN npm install -g @angular/cli@8 && \
    npm cache clean --force && \
    rm -rf ~/.npm

CMD ["./dev_start.sh"]
