#!/bin/bash

set -e  # exit on error

# This setup will install nodejs as well, which is not being used for the current
# phase, and would probably change in the future.

echo "Checking conda installation..."
if ! type conda > /dev/null; then
    echo "Please install conda"
    exit 1
fi

echo "Creating development environment for SRPMS project ..."
echo "Please specify the name for your new conda environment:"
read ENV_NAME

echo "Setting up environment..."
# ipython for easy access
conda create -n ${ENV_NAME} \
    python=3.7 \
    django=2.2 \
    postgresql=11 \
    psycopg2 \
    ipython \
    ldap3 \
    nodejs=10

# Allow conda activate in this script
source "$(dirname $(dirname $(which conda)))/etc/profile.d/conda.sh"

echo "Activating new environment..."
conda activate ${ENV_NAME}

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

echo "Finished!"
