#!/usr/bin/env bash

LPC_CONDOR_CONFIG=/etc/condor/config.d/01_cmslpc_interactive
LPC_CONDOR_LOCAL=/usr/local/bin/cmslpc-local-conf.py

cat <<EOF > shell
#!/usr/bin/env bash


if [ "\$1" == "" ]; then
  echo "We no longer have a default image. Please specify a coffea image."
  echo "Good choices would be:"
  echo " - coffeateam/coffea-dask-almalinux8:latest (for coffea CalVer)"
  echo " - coffeateam/coffea-base-almalinux8:latest (for coffea 0.7)"
  echo "All options can be enumerated by looking at either"
  echo " https://hub.docker.com/repositories/coffeateam"
  echo "or"
  echo " ls /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam"
  exit 1
else
  export COFFEA_IMAGE=\$1
fi

export APPTAINER_BINDPATH=${APPTAINER_BINDPATH}${APPTAINER_BINDPATH:+,}/uscmst1b_scratch,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,${LPC_CONDOR_CONFIG},${LPC_CONDOR_LOCAL}:${LPC_CONDOR_LOCAL}.orig,.cmslpc-local-conf:${LPC_CONDOR_LOCAL}

APPTAINER_SHELL=\$(which bash) apptainer exec -B \${PWD}:/srv --pwd /srv \\
  /cvmfs/unpacked.cern.ch/registry.hub.docker.com/\${COFFEA_IMAGE} \\
  /bin/bash --rcfile /srv/.bashrc
EOF

cat <<EOF > .cmslpc-local-conf
#!/bin/bash
python3 ${LPC_CONDOR_LOCAL}.orig | grep -v "LOCAL_CONFIG_FILE"
EOF

cat <<EOF > .bashrc
LPCJQ_VERSION="0.4.1"
install_env() {
  set -e
  echo "Installing shallow virtual environment in \$PWD/.env..."
  python -m venv --without-pip --system-site-packages .env
  unlink .env/lib64  # HTCondor can't transfer symlink to directory and it appears optional
  # work around issues copying CVMFS xattr when copying to tmpdir
  export TMPDIR=\$(mktemp -d -p .)
  .env/bin/python -m ipykernel install --user
  rm -rf \$TMPDIR && unset TMPDIR
  .env/bin/python -m pip install -q git+https://github.com/CoffeaTeam/lpcjobqueue.git@v\${LPCJQ_VERSION}
  echo "done."
  set +e
}

export CONDOR_CONFIG=${LPC_CONDOR_CONFIG}
export JUPYTER_PATH=/srv/.jupyter
export JUPYTER_RUNTIME_DIR=/srv/.local/share/jupyter/runtime
export JUPYTER_DATA_DIR=/srv/.local/share/jupyter
export IPYTHONDIR=/srv/.ipython
unset GREP_OPTIONS

[[ -d .env ]] || install_env
source .env/bin/activate
alias pip="python -m pip"
pip show lpcjobqueue 2>/dev/null | grep -q "Version: \${LPCJQ_VERSION}" || pip install -q git+https://github.com/CoffeaTeam/lpcjobqueue.git@v\${LPCJQ_VERSION}
EOF

chmod u+x shell .bashrc .cmslpc-local-conf
echo "Wrote shell and .bashrc to current directory. You can delete this file. Run ./shell to start the apptainer shell"
