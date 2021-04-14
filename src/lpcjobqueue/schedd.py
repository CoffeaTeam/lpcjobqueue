import logging
import os
import re


logger = logging.getLogger(__name__)
os.environ["CONDOR_CONFIG"] = os.path.join(os.path.dirname(__file__), "condor_config")
import htcondor  # noqa: E402


def acquire_schedd():
    """Acquire a htcondor.Schedd object

    Uses the bundled condor_config to connect to the LPC pool, query available schedds,
    and use the custom `condor_submit` schedd-choosing algorithm to select a schedd for
    this session. This function will not return the same value, so keep it around until
    all jobs are removed!
    """
    remotePool = re.findall(
        r"[\w\/\:\/\-\/\.]+", htcondor.param.get("FERMIHTC_REMOTE_POOL")
    )
    collector = None
    scheddAds = None
    for node in remotePool:
        try:
            collector = htcondor.Collector(node)
            scheddAds = collector.query(
                htcondor.AdTypes.Schedd,
                projection=[
                    "Name",
                    "MyAddress",
                    "MaxJobsRunning",
                    "ShadowsRunning",
                    "RecentDaemonCoreDutyCycle",
                    "TotalIdleJobs",
                ],
                constraint='FERMIHTC_DRAIN_LPCSCHEDD=?=FALSE && FERMIHTC_SCHEDD_TYPE=?="CMSLPC"',
            )
            if scheddAds:
                break
        except Exception:
            logger.debug(f"Failed to contact pool node {node}, trying others...")
            pass

    if not scheddAds:
        raise RuntimeError("No pool nodes could be contacted")

    weightedSchedds = {}
    for schedd in scheddAds:
        # covert duty cycle in percentage
        scheddDC = schedd["RecentDaemonCoreDutyCycle"] * 100
        # calculate schedd occupancy in terms of running jobs
        scheddRunningJobs = (schedd["ShadowsRunning"] / schedd["MaxJobsRunning"]) * 100

        logger.debug("Looking at schedd: " + schedd["Name"])
        logger.debug(f"DutyCyle: {scheddDC}%")
        logger.debug(f"Running percentage: {scheddRunningJobs}%")
        logger.debug(f"Idle jobs: {schedd['TotalIdleJobs']}")

        # Calculating weight
        # 70% of schedd duty cycle
        # 20% of schedd capacity to run more jobs
        # 10% of idle jobs on the schedd (for better distribution of jobs across all schedds)
        weightedSchedds[schedd["Name"]] = (
            (0.7 * scheddDC)
            + (0.2 * scheddRunningJobs)
            + (0.1 * schedd["TotalIdleJobs"])
        )

    schedd = min(weightedSchedds.items(), key=lambda x: x[1])[0]
    schedd = collector.locate(htcondor.DaemonTypes.Schedd, schedd)
    return htcondor.Schedd(schedd)


# Pick a schedd once on import
# Would prefer one per cluster but there is a quite scary weakref.finalize
# that depends on it
SCHEDD = acquire_schedd()
