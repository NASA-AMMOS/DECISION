import sys
sys.path.append('../')

import os
import shutil

from contextvars            import copy_context
from dash._callback_context import context_value
from dash._utils            import AttributeDict
from sklearn                import datasets
from dash.html              import Br, H5

from decision.pages.summary import get_param_history
from decision.pages.summary import optimal_k
from decision.pages.summary import populate_pareto_front
from decision.pages.summary import download_selected_config_1
from decision.pages.summary import download_selected_config_2
from decision.pages.summary import update_analysis_cols

import numpy as np


def test_get_param_history():
    '''Test parsing Dakota output'''
    known_param_names = ['sigma', 'sigma_ratio', 'center_x', 'window_x', 'window_y', 'denoise_x', 'min_filtered_threshold', 'min_SNR_conv', 'min_peak_volume']
    param_names, param_data = get_param_history("test/data/dakota_data_test.dat")
    assert known_param_names == param_names


def test_optimal_k():
    '''Test determining optimal K value using knee curve strategy'''
    iris = datasets.load_iris()
    k_ = optimal_k(iris.data, 5)
    assert k_ == 2

def test_populate_pareto_front():

    pareto_store =  {'Maximize_Recall': [0.89772727273, 0.69318181818, 0.875, 0.90909090909, 0.71590909091, 0.52272727273], 'Maximize_Precision': [0.54482758621, 0.63541666667, 0.56617647059, 0.5, 0.62376237624, 0.54761904762]}
    dynamic_plots, cluster_table, summary_store, cluster_names_1,  cluster_names_1_default, cluster_names_2, cluster_names_2_default = populate_pareto_front(pareto_store)
    assert cluster_names_1 == ['A', 'B']
    assert cluster_names_2 == ['A', 'B']
    assert cluster_names_1_default == 'A'
    assert cluster_names_2_default == 'B'


def test_download_selected_config_1():

    n_clicks = 1
    output_file = download_selected_config_1(n_clicks)
    assert output_file['filename'] == 'DECISION_Summary_Report.pdf'
    assert output_file['base64'] == True

def test_download_selected_config_2():

    n_clicks = 1
    output_file = download_selected_config_2(n_clicks)
    assert output_file['filename'] == 'DECISION_Summary_Report.pdf'
    assert output_file['base64'] == True

def test_update_analysis_cols():
    summary_store = {'param_names': ['sigma', 'sigma_ratio', 'center_x', 'window_x', 'window_y', 'denoise_x', 'min_filtered_threshold', 'min_SNR_conv', 'min_peak_volume'], 'param_data': [[3, 3.05, 91, 156, 14, 91, 50, 10, 750], [4.459795782, 1.868016863, 39, 113, 14, 109, 92, 5, 1180], [2.002870959, 4.270898872, 133, 165, 12, 99, 89, 12, 983], [3.264871481, 2.752606606, 163, 166, 16, 138, 29, 10, 1409], [3.912280477, 3.730528776, 153, 155, 12, 113, 100, 13, 424], [2.543688538, 1.853931166, 48, 127, 15, 45, 89, 5, 933], [4.619026014, 2.045968484, 20, 186, 20, 84, 79, 9, 1079], [1.57511534, 3.014433007, 113, 166, 10, 60, 41, 10, 226], [2.314075666, 2.727978128, 47, 124, 17, 42, 91, 11, 1318]], 'closest': [3, 8], 'cluster_names': ['A', 'B'], 'metrics_data': [[0.89772727273, 0.54482758621], [0.69318181818, 0.63541666667], [0.875, 0.56617647059], [0.90909090909, 0.5], [0.71590909091, 0.62376237624], [0.52272727273, 0.54761904762], [0.60227272727, 0.68831168831], [0.90909090909, 0.36529680365], [0.65909090909, 0.68235294118]], 'metrics_names': ['Maximize Recall', 'Maximize Precision']}
    experiments_store = {'experiments': [2], 'experiment_names': ['190617_023']}
    dropdown_1 = "A"
    dropdown_2 = "B"
    ac_col_1_dropdown, ac_col_2_dropdown = update_analysis_cols(summary_store, experiments_store, dropdown_1, dropdown_2)
    assert len(ac_col_1_dropdown) == 10
    assert len(ac_col_2_dropdown) == 10
