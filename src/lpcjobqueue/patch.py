"""Patches to be applied to workers

"""
from dask.sizeof import sizeof
import uproot
import awkward


@sizeof.register(awkward.highlevel.Array)
@sizeof.register(uproot.model.Model)
def sizeof_uproot_generic(obj):
    return obj.num_bytes
