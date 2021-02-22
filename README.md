lpcjobqueue
===========
A dask-jobqueue plugin for the LPC Condor queue designed to work with the `coffea-dask` singularity image.


# Installation
From the working directory of your coffea project, download and run the boostrap script:
```bash
...
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
