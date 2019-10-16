# Deploy/Test configuration

This directory contains configurations for running docker-compose for production deployment or test
purpose. Refer to [deployment docs](../docs/Deployment.md) for more details about how to configure 
your machine.

NOTE: Please don't put any commend inside `*.env` files, neither block or inline, or they
will be read as part of the configuration, this is the designed behavior of docker-compose 
