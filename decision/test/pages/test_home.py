import sys
sys.path.append('../')

import os
import shutil

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict
from sklearn                import datasets
from dash.html              import Br, H5

from decision.pages.home import config_dropdown_callback

import numpy as np


def test_config_dropdown_callback():

	result = config_dropdown_callback("ACME")
	assert result[0]['config_name'] == 'ACME'
	assert result[0]['config_path'] == 'configs/ACME.yaml'

	result = config_dropdown_callback("AEGIS")
	assert result[0]['config_name'] == 'AEGIS'
	assert result[0]['config_path'] == 'configs/AEGIS.yaml'
