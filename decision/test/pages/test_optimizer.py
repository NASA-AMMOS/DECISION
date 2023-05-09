import sys
sys.path.append('../')

import os
import shutil
import filecmp

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.optimizer import update_dakota_inputs

def test_update_dakota_inputs():
    '''Test updating parameters in the Dakota input configuration file'''

    update_dict = {"max_iterations": 1,
                   "max_function_evaluations": 2,
                   "population_size": 3,
                   "mutation_rate": 4,
                   "crossover_rate": 5,
                   "replacement_type": 6}

    update_dakota_inputs(update_dict, "test/data/dakota_metrics_params.tmp", "test/data/dakota_input.tmp")
    assert filecmp.cmp("test/data/dakota_input_ref.tmp", "test/data/dakota_input.tmp") == True