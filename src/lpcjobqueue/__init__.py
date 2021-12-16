"""A dask-jobqueue plugin for the LPC Condor queue
"""
from .cluster import LPCCondorCluster, LPCCondorJob
from .version import version as __version__

__all__ = ["__version__", "LPCCondorJob", "LPCCondorCluster"]
