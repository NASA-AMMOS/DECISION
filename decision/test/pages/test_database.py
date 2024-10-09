import sys
sys.path.append('../')

import os
import shutil

from decision.pages.database import callbackExperimentStoreUpdate
from decision.pages.database import select_all

import numpy as np
import pytest
from unittest.mock import patch, mock_open
import shutil
import os
import yaml

# Mock configuration data
config_store_mock = {
    'config_path': 'fake_config_path.yaml',
    'config_name': 'test_config'
}

# Mock table data
table_data_mock = [
    {'ID': '123', 'name': 'Experiment 1', 'value': '10'},
    {'ID': '456', 'name': 'Experiment 2', 'value': '20'},
]

# Mock upload store data
upload_store_mock = {
    'experiments': ['Experiment 1']
}

# Mock selected experiments
selected_experiments_mock = ['Experiment 2']


@patch('builtins.open', new_callable=mock_open, read_data="data:\n  data_extension: 'csv'")
@patch('shutil.copy')
@patch('os.path.exists', return_value=False)  
@patch('os.mkdir')  
def test_callbackExperimentStoreUpdate(mock_mkdir, mock_exists, mock_copy, mock_open_file):
    # Call the callback function with the mocked data
    result = callbackExperimentStoreUpdate(
        selected_experiments=selected_experiments_mock, 
        upload_store=upload_store_mock, 
        table_data=table_data_mock, 
        config_store=config_store_mock
    )
    
    # Assert that the experiments list has been updated
    assert result['experiments'] == ['Experiment 1', 'Experiment 2']
    
    # Assert that other data fields from the table were included in the result
    assert result['ID'] == ['123', '456']
    assert result['name'] == ['Experiment 1', 'Experiment 2']
    assert result['value'] == ['10', '20']

