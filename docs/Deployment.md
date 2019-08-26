# First time configuration

## VM Clean up

```bash
# Since we are using docker, we'll disable un-necessary services
sudo systemctl disable nginx.service
sudo systemctl stop nginx.service
sudo systemctl disable postgresql.service
sudo systemctl stop postgresql.service
sudo pkill -U tomcat8
```

TODO: The VM currently have too many unrelated packages installed, need to further clean up the environment.

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

## First time deploy



# Deploy - Development

```bash
docker-compose run django-gunicorn python manage.py collectstatic --no-input

# If you don't have a database yet, please also run the following command
# docker-compose run django-gunicorn python manage.py migrate

docker-compose -f docker-compose.dev.yml up
```

# Deploy - Production 

```bash
docker-compose run django-gunicorn python manage.py collectstatic --no-input

# If you don't have a database yet, please also run the following command
# docker-compose run django-gunicorn python manage.py migrate

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

[Docker Compose with NginX, Django, Gunicorn and multiple Postgres databases](
https://pawamoy.github.io/2018/02/01/docker-compose-django-postgres-nginx.html
)

[Understanding Docker Networking Drivers and their use cases](https://blog.docker.com/2016/12/understanding-docker-networking-drivers-use-cases/)

## Docker

## Environment Variable priorities

1. Compose file
2. Shell environment variables
3. Environment file
4. Dockerfile
5. Variable is not defined

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
