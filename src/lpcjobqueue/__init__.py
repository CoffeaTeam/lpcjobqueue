"""A dask-jobqueue plugin for the LPC Condor queue
"""
from .version import version as __version__
from .cluster import LPCCondorJob, LPCCondorCluster

__all__ = ["__version__", "LPCCondorJob", "LPCCondorCluster"]
