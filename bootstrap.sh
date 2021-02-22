#!/usr/bin/env bash

cat <<EOF > shell
#!/usr/bin/env bash

singularity exec -B \${PWD}:/srv --pwd /srv \\
  /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest \\
  /bin/bash --rcfile /srv/.bashrc
EOF

cat <<EOF > .bashrc
install_env() {
  set -e
  echo "Installing shallow virtual environment in \$PWD/.env..."
  python -m venv --system-site-packages .env
  .env/bin/pip install -q git+https://github.com/CoffeaTeam/lpcjobqueue.git
  echo "done."
}

[[ -d .env ]] || install_env
source .env/bin/activate

export JUPYTER_PATH=/srv/.jupyter
export JUPYTER_RUNTIME_DIR=/srv/.local/share/jupyter/runtime
export JUPYTER_DATA_DIR=/srv/.local/share/jupyter
export IPYTHONDIR=/srv/.ipython
EOF

chmod u+x shell .bashrc
echo "Wrote shell and .bashrc to current directory. Run ./shell to start the singularity shell"
