import sys
sys.path.append('../')

import os
import shutil
import filecmp
import unittest
from dash import html, dcc

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.optimizer import update_optim_sliders



class TestUpdateOptimSliders(unittest.TestCase):

    def setUp(self):
        # Mock data for ga_store (configuration for sliders)
        self.ga_store = {
            "max_iterations": {
                "name": "Max Iterations",
                "description": "Maximum number of iterations.",
                "min": 100,
                "max": 1000,
                "step": 50,
                "default": 500
            },
            "max_function_evaluations": {
                "name": "Max Function Evaluations",
                "description": "Maximum number of function evaluations.",
                "min": 1000,
                "max": 10000,
                "step": 500,
                "default": 5000
            },
            "population_size": {
                "name": "Population Size",
                "description": "Size of the population.",
                "min": 10,
                "max": 100,
                "step": 5,
                "default": 50
            },
            "mutation_rate": {
                "name": "Mutation Rate",
                "description": "Rate of mutation.",
                "min": 0.01,
                "max": 0.1,
                "step": 0.01,
                "default": 0.05
            },
            "crossover_rate": {
                "name": "Crossover Rate",
                "description": "Rate of crossover.",
                "min": 0.1,
                "max": 1.0,
                "step": 0.1,
                "default": 0.5
            }
        }

    def test_no_update_dict(self):
        # Mock data for upload_store without update_dict
        upload_store = {
            "update_dict": {}
        }

        # Call the callback
        sliders = update_optim_sliders(upload_store, self.ga_store)

        # Assert that the returned sliders are correct
        self.assertEqual(len(sliders), 17)  # 5 sliders + headers/descriptions/buttons

    def test_update_dict(self):
        # Mock data for upload_store with update_dict
        upload_store = {
            "update_dict": {
                "max_iterations": 700,
                "max_function_evaluations": 8000,
                "population_size": 60,
                "mutation_rate": 0.08,
                "crossover_rate": 0.6
            }
        }

        # Call the callback
        sliders = update_optim_sliders(upload_store, self.ga_store)

        # Assert that the returned sliders are correct
        self.assertEqual(len(sliders), 17)  # 5 sliders + headers/descriptions/buttons


    def test_partial_update_dict(self):
        # Mock data for upload_store with partial update_dict
        upload_store = {
            "update_dict": {
                "max_iterations": 700,
            }
        }

        # Call the callback
        sliders = update_optim_sliders(upload_store, self.ga_store)


