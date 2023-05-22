import sys
sys.path.append('../')

import os
import shutil
import filecmp

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.optimizer import callbackButton
from decision.pages.optimizer import on_data
from decision.pages.optimizer import dakota_shutdown
from decision.pages.optimizer import callbackSliders

def test_callbackButton():

	data= callbackButton(1, None)
	assert data == {'clicks': 1}

def test_on_data():

	plots, status, metrics_dict = on_data(None, {'metrics': []}, 1)
	assert status == []
	assert metrics_dict == {}

	plots, status, metrics_dict = on_data(1684006626261, {'metrics': []}, 1)
	assert len(status) == 1


def test_dakota_shutdown():

	result = dakota_shutdown(2)
	assert result == ''

def test_callbackSliders():

	max_iterations = 300000
	max_function_evaluations = 300000
	population_size = 50
	mutation_rate = 1
	crossover_rate = 0
	replacement_size = 10
	replacement_type = "Elitist"
	parameters_store = {'parameters': [[11, 171], [111, 201], [7, 21], [31, 151], [1, 5], [1.1, 5], [0, 100], [5, 15], [0, 1500], [3, 3], [0.5, 0.5]]}
	metrics_store = {'metrics': ['Maximize Recall', 'Maximize Precision']}

	result = callbackSliders(max_iterations, max_function_evaluations, population_size, mutation_rate, crossover_rate, replacement_size,  replacement_type, parameters_store, metrics_store)
	assert result == ''
