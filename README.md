# Student Research Project Managment System - A COMP8755 Project

```
.
├── certbox/         # docker image for certbot (obtain HTTPS certificate)
├── config.dev/      # deployment configuration for development
├── config.prod/     # deployment configuration for production
├── docs/            # documentation
├── gitlab-ci/       # GitLab CI Runner docker image
├── nginx/           # nginx docker image
├── srpms/           # Django back-end code
├── srpms-client/    # Angular front-end code
├── tests/           # Some test utilities
├── .env             # Define environment variables that would be used for docker-compose
├── .gitignore       # git ignore configuration
├── .gitlab-ci.yml   # GitLab CI pipeline configurations
├── dev_setup.sh     # Local development environment setup
├── docker-compose.dev.yml            # Devlopment environment docker compose configration
├── docker-compose.prod.base.yml      # Share docker compose configuration between test and deployment
├── docker-compose.prod.deploy.yml    # Deployment (production) environment docker compose configration
├── docker-compose.prod.test.yml      # Test environment docker compose configration
└── README.md                         # This file
```

Please refer to [docs](docs/) for documentations.

For better coding experience, please use [Intellij IDEA](https://www.jetbrains.com/idea/) or 
[PyCharm](https://www.jetbrains.com/pycharm/) with Django and Angular plugin. 

For better reading experience and diagram support, please install [Typora](https://www.typora.io/)
