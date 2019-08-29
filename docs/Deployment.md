# First time configuration

**NOTICE: If you are doing this on your own machine, please start from [Database migration](#database-migration)**

## VM Clean up

```bash
# For srpms.cecs.anu.edu.au only
# Since we are using docker, we'll disable un-necessary services
sudo systemctl disable nginx.service
sudo systemctl stop nginx.service
sudo systemctl disable postgresql.service
sudo systemctl stop postgresql.service
sudo pkill -U tomcat8
```

TODO: The VM currently has too many unrelated packages installed, need to further clean up the environment.

## Install docker

```bash
sudo apt-get update

# Install packages to allow apt to use a repository over HTTPS
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -


# Setup the stable repository
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

# Update apt and install docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## Configure iptable

```bash
sudo apt-get install iptables-persistent

# Put the iptables rule under corresponding folder
#mv iptable-rules /etc/iptables/rules.v4

# Let docker reload its iptables rules
sudo systemctl restart docker.service

# Reload the configuration
sudo systemctl restart netfilter-persistent
```

## Configure repository for group access

```bash
# Create folder at root for group access
sudo mkdir /srpms
sudo addgroup srpms
sudo chown root:srpms /srpms
sudo chmod g+w /srpms

# Download source code
git clone https://gitlab.cecs.anu.edu.au/u6513788/comp8755-srpms.git .
# Configure git for group access
git config core.sharedRepository group
# Change file ownership and permission to allow group access
chgrp -R srpms .
chmod -R g+w .
# Git pack files should be immutable
chmod g-w objects/pack/*
# Configure new file to inherit directory's group id
find -type d -exec chmod g+s {} +
```

## CI/CD

**NOTICE: For this project we only consider docker as [executor](https://docs.gitlab.com/runner/executors/)**

```bash
# Pull gitlab runner image
docker image pull gitlab/gitlab-runner:alpine

# Register, you'll need token from "Settings" -> "CI/CD" -> "Runner" page of the srpms repo in order to register a runner.
cd /srpms/gitlab-ci
docker-compose run runner register

# Start the runner
docker-compose up -d
```

## Database migration

**WARNING: Please make sure there is no database under the same name before operate**

- If you already have a database dump name `<db_dump>`, you can import it to the database container by
  1. Copy to the database container
     `docker cp <db_dump> srpms_db-postgres:/`
  2. Import to the database
     `docker-compose -f <compose file> run db-postgres psql -U <db_name> < /<db_dump>`
- If you wants to initialize a new database
  `docker-compose -f <compose file> run django-gunicorn python manage.py migrate`

# Deploy - Development

**Please make sure you are under the project directory when using following commands**

```bash
# Start, use -d if you want to run in background
docker-compose -f docker-compose.dev.yml up

# Clean-up containers
docker-compose -f docker-compose.dev.yml down
```

The about command would

- Listen at `localhost:8000` for HTTP
- Listen at `localhost:8001` for HTTPS
- `/media/`, `/static/`, `/api/` would be directed to Django container
- All other requests would be directed to the Angular container

To attach to a running container, use `docker exec -it <service_name> <command>`

- For example, to attach to the Django container for debugging, use command
  `docker exec -it django-gunicorn_1 /bin/sh`

To run a single container with some command, use `docker-compose -f <compose file> run <service_name> <command>`

- Using this command has the advantage over regular `docker run`, as it will apply settings specified in the docker-compose file

# Deploy - Production

**Under construction, do NOT attempt**

```bash
# Collect static files
docker-compose run django-gunicorn python manage.py collectstatic --no-input

docker-compose -f docker-compose.prod.yml -d up
```


## Caveats

### Disable the REST browsable API on production

Simple add the following to the `settings.py`
```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
```

[Refer to here](http://masnun.com/2016/04/20/django-rest-framework-remember-to-disable-web-browsable-api-in-production.html) for the reason of doing so.

# Reference 

[How to configure an existing git repo to be shared by a UNIX group](https://stackoverflow.com/questions/3242282/how-to-configure-an-existing-git-repo-to-be-shared-by-a-unix-group)

[How To Get Angular and Nginx Working Together Properly for Development](https://medium.com/better-programming/how-to-properly-get-angular-and-nginx-working-together-for-development-3e5d158734bf)

## Docker

- Environment Variable priorities when using compose
  1. Compose file
  2. Shell environment variables
  3. Environment file
  4. Dockerfile
  5. Variable is not defined

[Building Django Docker Image with Alpine](https://medium.com/c0d1um/building-django-docker-image-with-alpine-32de65d2706)

[Docker Compose with NginX, Django, Gunicorn and multiple Postgres databases](
https://pawamoy.github.io/2018/02/01/docker-compose-django-postgres-nginx.html
)

[Understanding Docker Networking Drivers and their use cases](https://blog.docker.com/2016/12/understanding-docker-networking-drivers-use-cases/)

[Deploying Gunicorn](http://docs.gunicorn.org/en/latest/deploy.html)

[Deploying nginx + django + python 3](https://tutos.readthedocs.io/en/latest/source/ndg.html)

## SSL certificates

To generate a self-signed SSL certificate for `localhost` (for development purpose)

```
openssl req -x509 -out localhost.crt -keyout localhost.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```

This self-sign certificate would not accept by chrome, as such, you need to go to `chrome://flags/#allow-insecure-localhost`, and set it to `enable`



[How to Setup a SSL Certificate on Nginx for a Django Application](https://simpleisbetterthancomplex.com/tutorial/2016/05/11/how-to-setup-ssl-certificate-on-nginx-for-django-application.html)

[Nginx and Let’s Encrypt with Docker in Less Than 5 Minutes](https://medium.com/@pentacent/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)

[Certificates for localhost](https://letsencrypt.org/docs/certificates-for-localhost/)

## CI/CD

[Getting started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)

[Run GitLab Runner in a container](https://docs.gitlab.com/runner/install/docker.html)

[Register Runners](https://docs.gitlab.com/runner/register/index.html#docker)

## Server iptables rule

```
# Title: iptables rules for SRPMS Server
# Author: Dajie Yang
# Last Modify: Aug 23 2019

################
# Mangle Table #
################
# *mangle

################
# Filter Table #
################
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]
:addrtype-general - [0:0]
:anti-scan - [0:0]
:app-limit - [0:0]
:app-reject - [0:0]
# Allow all loopback traffic
-A INPUT -i lo -j ACCEPT
-A OUTPUT -o lo -j ACCEPT
# Quickly process packets for which we already have a connection
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A OUTPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Drop INVALID packets
-A INPUT -m conntrack --ctstate INVALID -m limit --limit 3/min --limit-burst 10 -j LOG --log-prefix "[INVALID] "
-A INPUT -m conntrack --ctstate INVALID -j DROP
# Ok icmp codes for INPUT
-A INPUT -p icmp --icmp-type destination-unreachable -j ACCEPT
-A INPUT -p icmp --icmp-type source-quench -j ACCEPT
-A INPUT -p icmp --icmp-type time-exceeded -j ACCEPT
-A INPUT -p icmp --icmp-type parameter-problem -j ACCEPT
-A INPUT -p icmp --icmp-type echo-request -j ACCEPT
# Ok icmp code for FORWARD
-A FORWARD -p icmp --icmp-type destination-unreachable -j ACCEPT
-A FORWARD -p icmp --icmp-type source-quench -j ACCEPT
-A FORWARD -p icmp --icmp-type time-exceeded -j ACCEPT
-A FORWARD -p icmp --icmp-type parameter-problem -j ACCEPT
-A FORWARD -p icmp --icmp-type echo-request -j ACCEPT
-A FORWARD -p icmp --icmp-type echo-reply -j ACCEPT
# Allow DHCP client to work
-A INPUT -p udp --sport 67 --dport 68 -j ACCEPT
# Procss special address, generally
-A INPUT -j addrtype-general
-A addrtype-general -m addrtype --dst-type LOCAL -j RETURN
-A addrtype-general -m addrtype --dst-type MULTICAST -j RETURN
-A addrtype-general -m addrtype --dst-type BROADCAST -j RETURN
-A addrtype-general -m addrtype --dst-type UNICAST -j DROP
-A addrtype-general -m limit --limit 3/min --limit-burst 10 -j LOG --log-prefix "[SPECIAL ADDR] "
-A addrtype-general -j DROP
# allow MULTICAST mDNS for service discovery
-A INPUT -p udp -d 224.0.0.251 --dport 5353 -j ACCEPT
# allow MULTICAST UPnP for service discovery
-A INPUT -p udp -d 239.255.255.250 --dport 1900 -j ACCEPT
# Blocking port scan
-A INPUT -p tcp --tcp-flags ACK,FIN FIN -j anti-scan
-A INPUT -p tcp --tcp-flags ACK,PSH PSH -j anti-scan
-A INPUT -p tcp --tcp-flags ACK,URG URG -j anti-scan
-A INPUT -p tcp --tcp-flags ALL ALL -j anti-scan
-A INPUT -p tcp --tcp-flags ALL NONE -j anti-scan
-A INPUT -p tcp --tcp-flags ALL SYN,RST,ACK,FIN,URG -j anti-scan
-A INPUT -p tcp --tcp-flags SYN,FIN SYN,FIN -j anti-scan
-A INPUT -p tcp --tcp-flags FIN,RST FIN,RST -j anti-scan
-A INPUT -p tcp --tcp-flags ALL SYN,FIN -j anti-scan
-A INPUT -p tcp --tcp-flags ALL URG,PSH,FIN -j anti-scan
-A INPUT -p tcp --tcp-flags ALL FIN -j anti-scan
-A INPUT -p tcp --tcp-flags ALL URG,PSH,SYN,FIN -j anti-scan
-A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j anti-scan
-A anti-scan -m limit --limit 3/min --limit-burst 3 -j LOG --log-prefix "[PORT SCAN] "
-A anti-scan -m recent --set --name PORT-SCAN --mask 255.255.255.255 --rsource
-A anti-scan -m recent --update --seconds 30 --hitcount 10 --name PORT-SCAN --mask 255.255.255.255 --rsource -j DROP
# Exception for applications
# SSH
-A INPUT -p tcp -m tcp --dport 22 -j LOG --log-prefix "[SSH] "
-A INPUT -p tcp -m tcp --dport 22 -j app-limit
# HTTP/HTTPS, does not currently apply any connection limit
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -p udp -m udp --dport 80 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT
-A INPUT -p udp -m udp --dport 443 -j ACCEPT
# Limit connection frequency to 10 hits per 30s, after that block the client for 5 minutes
-A app-limit -m conntrack --ctstate NEW -m recent --set --name APP-LIMIT --mask 255.255.255.255 --rsource
-A app-limit -m conntrack --ctstate NEW -m recent --update --seconds 30 --hitcount 10 --name APP-LIMIT --mask 255.255.255.255 --rsource -j app-reject
-A app-limit -j ACCEPT
-A app-reject -m limit --limit 5/min -j LOG --log-prefix "[APP REJECT] "
-A app-reject -j REJECT --reject-with icmp-port-unreachable
COMMIT
# Done
```
