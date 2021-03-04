import time
from dask.distributed import Client
from lpcjobqueue import LPCCondorCluster
from coffea import hist, processor, nanoevents
import awkward as ak


class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = processor.dict_accumulator(
            {
                "sumw": processor.defaultdict_accumulator(float),
                "mass": hist.Hist(
                    "Events",
                    hist.Cat("dataset", "Dataset"),
                    hist.Bin("mass", r"$m_{\mu\mu}$ [GeV]", 60, 60, 120),
                ),
            }
        )

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.identity()

        dataset = events.metadata["dataset"]
        muons = events.Muon

        cut = (ak.num(muons) == 2) & (ak.sum(muons.charge, axis=-1) == 0)
        # add first and second muon in every event together
        dimuon = muons[cut][:, 0] + muons[cut][:, 1]

        output["sumw"][dataset] += len(events)
        output["mass"].fill(
            dataset=dataset,
            mass=dimuon.mass,
        )

        return output

    def postprocess(self, accumulator):
        return accumulator


if __name__ == "__main__":
    tic = time.time()
    cluster = LPCCondorCluster()
    cluster.adapt(minimum=0, maximum=10)
    client = Client(cluster)

    fileset = {
        "DoubleMuon": [
            "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/Run2012B_DoubleMuParked.root",
            "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/Run2012C_DoubleMuParked.root",
        ],
        "ZZ to 4mu": [
            "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/ZZTo4mu.root"
        ],
    }

    exe_args = {
        "client": client,
        "savemetrics": True,
        "schema": nanoevents.NanoAODSchema,
        "align_clusters": True,
    }

    proc = MyProcessor()

    hists, metrics = processor.run_uproot_job(
        fileset,
        treename="Events",
        processor_instance=proc,
        executor=processor.dask_executor,
        executor_args=exe_args,
    )

    elapsed = time.time() - tic
    print(f"Output: {hists}")
    print(f"Metrics: {metrics}")
    print(f"Finished in {elapsed}s")
    print(f"Events/s: {metrics['entries'].value / elapsed}s")
