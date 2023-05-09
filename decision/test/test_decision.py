import sys
sys.path.append('../')

import os
import shutil

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict

from decision.decision import rebuild_folder

def test_rebuild_folder():
    '''Test dynamic folder creation and destruction'''
    test_path = "test/test/"
    if not os.path.exists(test_path):
        os.makedirs(test_path)

    rebuild_folder(test_path)
    assert os.path.isdir(test_path) == True
    shutil.rmtree(test_path)
