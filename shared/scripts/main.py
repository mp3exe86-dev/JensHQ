import sys
import os

# ROOT = C:/JobAgent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from jobagent.agents.jobfinder_agent import run_jobfinder
from jobagent.agents.tarif_analyzer_agent import run_tarif_analyzer

print("JobAgent gestartet")

run_jobfinder()
run_tarif_analyzer()

print("Fertig")