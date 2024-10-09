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

    # Test case 1: When 'upload-store' has data (takes precedence over config-dropdown value)
    upload_store_data = {'config_name': 'TEST', 'config_path': 'path/to/test.yaml'}
    config_value = 'ACME'  # This should be ignored when upload_store has data
    result = config_dropdown_callback(config_value, upload_store_data)
    assert result == {'config_name': 'TEST', 'config_path': 'path/to/test.yaml'}, f"Unexpected result: {result}"

    # Test case 2: When 'config-dropdown' is ACME and 'upload-store' is None
    result = config_dropdown_callback('ACME', None)
    assert result == {'config_name': 'ACME', 'config_path': 'configs/ACME.yaml'}, f"Unexpected result: {result}"

    # Test case 3: When 'config-dropdown' is AEGIS and 'upload-store' is None
    result = config_dropdown_callback('AEGIS', None)
    assert result == {'config_name': 'AEGIS', 'config_path': 'configs/AEGIS.yaml'}, f"Unexpected result: {result}"

    # Test case 4: When 'upload-store' has an empty dict (edge case)
    result = config_dropdown_callback('ACME', {})
    assert result == {'config_name': 'ACME', 'config_path': 'configs/ACME.yaml'}, f"Unexpected result: {result}"
