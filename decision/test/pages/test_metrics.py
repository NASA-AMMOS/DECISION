import sys
sys.path.append('../')

import os
import shutil
import filecmp

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.metrics import callback
from decision.pages.metrics import initial_callback
from decision.pages.metrics import update_runtime_estimate
from decision.pages.metrics import get_param_max_ranges


def test_callback():

	data, alerts = callback(['Maximize Recall', 'Maximize Precision'])
	assert data['metrics'] == ['Maximize Recall', 'Maximize Precision']
	assert alerts == []

def test_initial_callback():

	metrics = None
	config_store = {'config_name': 'ACME', 'config_path': 'configs/ACME.yaml'}
	blocks, metrics_list = initial_callback(metrics, config_store)

def test_update_runtime_estimate():

	slider_values = [[11, 171], [111, 201], [7, 21], [31, 151], [1, 5], [1.1, 5], [0, 100], [5, 15], [0, 1500], [3, 3], [0.5, 0.5]]
	config_store = {'config_name': 'ACME', 'config_path': 'configs/ACME.yaml'}
	progress_bar, data = update_runtime_estimate(slider_values, config_store)
	assert data['parameters'] == [[11, 171], [111, 201], [7, 21], [31, 151], [1, 5], [1.1, 5], [0, 100], [5, 15], [0, 1500], [3, 3], [0.5, 0.5]]

def test_get_param_max_ranges():

	param_ranges = get_param_max_ranges("configs/ACME.yaml")
	assert param_ranges == [[11, 171], [111, 201], [7, 21], [31, 151], [1, 5], [1.1, 5], [0, 100], [5, 15], [0, 1500], [0, 6], [0, 1]]