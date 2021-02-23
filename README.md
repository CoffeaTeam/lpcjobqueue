lpcjobqueue
===========
A dask-jobqueue plugin for the LPC Condor queue designed to work with the `coffea-dask` singularity image.


# Installation
From the working directory of your coffea project, download and run the boostrap script:
```bash
curl -OL https://raw.githubusercontent.com/CoffeaTeam/lpcjobqueue/main/bootstrap.sh
bash bootstrap.sh
```
The `./shell` executable can then be used to start a singularity shell.

# Usage
The singularity shell can spawn dask clusters on the LPC condor farm, using the same image for the workers
as the shell environment. You might need to `kinit` from within the container, and be sure your x509 proxy is up to date.

Example usage:
```python
from dask.distributed import Client
from lpcjobqueue import LPCCondorCluster


cluster = LPCCondorCluster()
cluster.scale(10)
client = Client(cluster)
# run_uproot_job(...)
```

There is a self-contained simple example in `simple_example.py`, you can run it on an LPC login node by doing:
```bash
./shell
curl -OL https://raw.githubusercontent.com/CoffeaTeam/lpcjobqueue/main/simple_example.py
python -i simple_example.py
# wait for it to run and finish
import coffea
coffea.util.save(hists, 'simple_hists.coffea') # plot and such elsewhere / at your leisure
exit()
exit
```
