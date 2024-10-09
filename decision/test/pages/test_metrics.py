import sys
sys.path.append('../')

import os
import shutil
import filecmp
import pytest
import yaml
import unittest

from unittest.mock          import mock_open, patch
from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.metrics import get_param_info

class TestGetParamInfo(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_get_param_info(self, mock_yaml_load, mock_file):
    	
        # Prepare mock data
        config_data = {
            'parameters': [
                {
                    'parameters': [
                        {'type': 'range', 'step': 0.1, 'name': 'Param 1'},
                        {'type': 'range', 'step': 1, 'variable_name': 'Variable_A'},
                        {'type': 'other', 'name': 'Not_Range_Param'}
                    ]
                },
                {
                    'parameters': [
                        {'type': 'range', 'step': 2.0, 'name': 'Param 2'}
                    ]
                }
            ]
        }

        # Mock the yaml.safe_load to return the config_data
        mock_yaml_load.return_value = config_data

        # Set up config_store mock
        config_store = {'config_path': 'mock_config.yaml'}

        # Call the function
        step_types, names = get_param_info(config_store)

        # Assert the expected results
        expected_step_types = ['continuous', 'discrete', 'continuous']
        expected_names = ['param_1', 'Variable_A', 'param_2']

        self.assertEqual(step_types, expected_step_types)
        self.assertEqual(names, expected_names)

        # Ensure file was opened correctly
        mock_file.assert_called_once_with(config_store['config_path'])