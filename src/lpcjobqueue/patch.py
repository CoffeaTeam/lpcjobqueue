"""Patches to be applied to workers

"""
import awkward
import uproot
import hist
from dask.sizeof import sizeof


@sizeof.register(awkward.highlevel.Array)
def sizeof_awkward_generic(obj):
    return obj.nbytes


@sizeof.register(uproot.model.Model)
def sizeof_uproot_generic(obj):
    return obj.num_bytes


@sizeof.register(hist.hist.Hist)
def sizeof_hist(obj):
    # doesn't include axes but that should be relatively small
    return sizeof(obj.view(flow=True))
