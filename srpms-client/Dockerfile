FROM node:10-alpine

ARG DEBUG

# Arbitrary location choice
RUN mkdir -p /app/srpms-client
WORKDIR /app/srpms-client

# Install angular
RUN npm install -g @angular/cli@8 && \
    npm cache clean --force && \
    rm -rf ~/.npm

COPY ./* ./
RUN if [ "$DEBUG" == "True" ]; then echo "Debug, skip build"; else ng build --prod; fi

CMD ["./start.sh"]