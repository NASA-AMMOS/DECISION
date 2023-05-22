import sys
sys.path.append('../')

import os
import shutil

from decision.pages.database import callbackExperimentStoreUpdate
from decision.pages.database import select_all

import numpy as np

def test_callbackExperimentStoreUpdate():

	data, alerts = callbackExperimentStoreUpdate([2])
	assert data == {'experiments': [2], 'experiment_names': ['190617_023']}
	assert alerts == []

def test_callbackExperimentStoreUpdate_noexperiments():

	data, alerts = callbackExperimentStoreUpdate([])
	assert data == {'experiments': []}
	assert len(alerts) == 1



