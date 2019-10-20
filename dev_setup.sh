#!/bin/bash
# Environment setup for development, only works for Debian-based system (Debian, Ubuntu, e.g.)
# Require conda installation for python environment management.
#
# Author: Dajie Yang (u6513788)
# Email: dajie.yang@anu.edu.au

set -e  # exit on error

# This setup will install nodejs as well, which is not being used for the current
# phase, and would probably change in the future.

echo
echo " ----------------------- IMPORTANT NOTICE ---------------------- "
echo "| This script is used for setting up local development envir-   |"
echo "| onment for the SRPMS project, do NOT use this for production. |"
echo " --------------------------------------------------------------- "
echo

echo "Checking conda installation..."
if ! type conda > /dev/null; then
    echo "Please install conda and configure \"conda activate\" first, \
          refer https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# TODO: is there any way we can include this in conda? because apt-get is only available for Debian
echo "Installing dependencies for LDAP authentication backend ..."
sudo apt-get install -y libsasl2-dev libldap2-dev build-essential libcairo2 libpango-1.0-0 \
     libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

echo "Creating development environment for SRPMS project ..."
echo "Please specify the name for your new conda environment:"
read ENV_NAME

echo "Setting up environment..."
# ipython for easy access
conda create -y -n ${ENV_NAME} \
    python=3.7 \
    django=2.2 \
    postgresql=11 \
    psycopg2 \
    ipython \
    ldap3 \
    nodejs=10 \
    cairo \
    pango

# Allow conda activate in this script
source "$(dirname $(dirname $(which conda)))/etc/profile.d/conda.sh"

echo "Activating new environment..."
conda activate ${ENV_NAME}

echo "Installing Django rest framework..."
pip install djangorestframework==3.10.*
pip install django-auth-ldap==2.0.*               # LDAP authentication support
pip install django-filter==2.2.*                  # Filtering support for fields
pip install markdown==3.1.*                       # Markdown support for the browsable API.
pip install djangorestframework_simplejwt==4.3.*  # API authentication support
pip install django-cors-headers==3.1.*            # Prevent CORS attach
pip install drf-extensions==0.5.*                 # Support nested API url
pip install WeasyPrint==50.*                      # Support contract PDF export
pip install coverage==4.5.*                       # Optional, for showing test coverage

echo "Setting environment specific variables..."
cd ${CONDA_PREFIX}
mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d
touch ./etc/conda/activate.d/nodejs_vars.sh
touch ./etc/conda/deactivate.d/nodejs_vars.sh

cat > ./etc/conda/activate.d/nodejs_vars.sh << EOF
#!/bin/sh

export NODE_PATH="${CONDA_PREFIX}/lib/node_modules"
EOF

cat > ./etc/conda/deactivate.d/nodejs_vars.sh << EOF
#!/bin/sh

unset NODE_PATH
EOF

echo "Finished! Please activate the environment by \"conda activate ${ENV_NAME}\""
