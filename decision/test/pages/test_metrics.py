import sys
sys.path.append('../')

import os
import shutil
import filecmp

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.pages.metrics import update_dakota_metrics_and_params


def test_update_dakota_metrics_and_params():
        '''Test updating Dakota input file with values from metrics page slider bars'''
        update_dakota_metrics_and_params(["Metric 1", "Metric 2"], 
                                         [1,2], 
                                         [3,4], 
                                         [5,6], 
                                         [7,8], 
                                         [9,10], 
                                         [11,12], 
                                         [13,14], 
                                         [15,16], 
                                         [17,18], 
                                         [19,20], 
                                         [21,22],
                                         "dakota_input.template",
                                         'test/data/dakota_metrics_params.tmp')

        assert filecmp.cmp('test/data/dakota_metrics_params_ref.tmp', 'test/data/dakota_metrics_params.tmp') == True