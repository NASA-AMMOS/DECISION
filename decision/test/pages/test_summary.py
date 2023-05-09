import sys
sys.path.append('../')

import os
import shutil

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict
from sklearn                import datasets

from decision.pages.summary import get_param_history
from decision.pages.summary import optimal_k

import numpy as np


def test_get_param_history():
	'''Test parsing Dakota output'''
	known_param_names = ['sigma', 'sigma_ratio', 'center_x', 'window_x', 'window_y', 'denoise_x', 'min_filtered_threshold', 'min_SNR_conv', 'min_peak_volume', 'Maximize_Precision']
	param_names, param_data = get_param_history("test/data/dakota_data_test.dat")
	assert known_param_names == param_names
	assert (np.load("test/data/param_data.npy") == param_data).all()

def test_optimal_k():
	'''Test determining optimal K value using knee curve strategy'''
	iris = datasets.load_iris()
	k_ = optimal_k(iris.data, 5)
	assert k_ == 2