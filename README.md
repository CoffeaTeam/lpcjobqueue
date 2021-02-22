lpcjobqueue
===========
A dask-jobqueue plugin for the LPC Condor queue.

Example usage:
```python
from dask.distributed import Client
from lpcjobqueue import LPCCondorCluster


cluster = LPCCondorCluster()
client = Client(cluster)
```
