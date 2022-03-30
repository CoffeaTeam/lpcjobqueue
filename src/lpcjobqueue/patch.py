"""Patches to be applied to workers

"""
import awkward
import uproot
from dask.sizeof import sizeof


@sizeof.register(awkward.highlevel.Array)
def sizeof_uproot_generic(obj):
    return obj.nbytes


@sizeof.register(uproot.model.Model)
def sizeof_uproot_generic(obj):
    return obj.num_bytes
