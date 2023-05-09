import dash
import os
import shutil

from dash.exceptions import PreventUpdate
from dash            import html
from dash            import dash_table
from dash            import callback
from dash            import Input
from dash            import Output
from dash            import State
from dash            import dcc

import dash_bootstrap_components as dbc
import pandas                    as pd


dash.register_page(__name__, title="Database")

df = pd.read_csv("experiments.csv")

layout = html.Div([

    # TODO - figure out better solution to this. These 9 ids are pre-declarations of ids used on the optimizer
    #           page.  Since the metrics-store is updated here, this triggers the optimizer page callback, which
    #           has metrics-store as an input.  This causes a callback warning, since these ids haven't been declared
    #           yet.  Pre-declaring them here to avoid the callback warning.  Seems to be a common Dash issue.
    dcc.Store(id='start_button_memory'),
    html.P(id='interval-component'),
    html.P(id='plots'),
    html.P(id='dakota-status'),
    html.Div(id='pareto-graph', style= {'display': 'none'}),
    html.Div(id='cluster-table', style= {'display': 'none'}),
    html.Div(id='dropdown_col_1', style= {'display': 'none'}),
    html.Div(id='dropdown_col_2', style= {'display': 'none'}),
    html.P(id='max_iterations'),
    html.P(id='max_function_evaluations'),
    html.P(id='population_size'), 
    html.P(id='mutation_rate'),
    html.P(id='crossover_rate'),
    html.P(id='replacement_size'),
    html.P(id='replacement_type'),
    html.Div(id='runtime_bar', style={'display': 'none'}),

    html.Div(
        className="db-header",
        children=[
            
            html.Div(
            html.H3("Select Experiments To Optimize With"),
            ),
            html.Div(
                children=[
                    dbc.Button("Select All Experiments", size='sm', id='select-all-button', style={"margin-right": "5px"}),
                    dbc.Button("Deselect All Experiments", size='sm', id='deselect-all-button'),
                    html.Br(),
                ]),
    ], style={'padding': 10, 'flex': 1, }),

    html.Div(children=[
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            row_selectable="multi",
            row_deletable=False,
            editable=False,
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "scroll"},
            style_cell={'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 10
            }),

    ], style={'padding': 20, 'flex': 1, 'font_family': 'Gill Sans'}),  

    html.Br(),
    html.Br(),
    html.H3("System Notifications"),
    html.Br(),
    html.Div(id='database-alerts'),

], style={'display': 'flex', 'flex-direction': 'column'})


@callback(
    [
        Output('table', 'selected_rows')
    ],[
        Input('select-all-button', 'n_clicks'),
        Input('deselect-all-button', 'n_clicks')
    ],[
        State('table', 'data'),
        State('table', 'derived_virtual_data'),
        State('table', 'derived_virtual_selected_rows')
    ]
)
def select_all(select_n_clicks, deselect_n_clicks, original_rows, filtered_rows, selected_rows):
    ctx = dash.callback_context.triggered[0]
    ctx_caller = ctx['prop_id']
    if filtered_rows is not None:
        if ctx_caller == 'select-all-button.n_clicks':
            selected_ids = [row for row in filtered_rows]
            return [[i for i, row in enumerate(original_rows) if row in selected_ids]]
        if ctx_caller == 'deselect-all-button.n_clicks':
            return [[]]
        raise PreventUpdate
    else:
        raise PreventUpdate


@callback(
    [
        Output('experiments-store', 'data'),
        Output('database-alerts', 'children')
    ],[
        Input('table', 'derived_virtual_selected_rows')
    ]
)
def callbackExperimentStoreUpdate(selected_experiments):

    # colors: success (green), warning (yellow), danger (red) 
    alerts = []
    experiment_names = []

    data = {"experiments": selected_experiments}

    if selected_experiments is None or selected_experiments == []:
        alerts.append(dbc.Alert("Please select at least one observation to optimize with", color="danger"))
        return data, alerts

    # make a copy of each selected observation in tmp directory for processing
    for x in range(0, len(selected_experiments)):
        product_ID = df['ID'][selected_experiments[x]]

        # TODO - put in config during generalization activity
        shutil.copy(os.path.join("data/ACME_Demo_Data/pickles",f"{product_ID}.pickle"),os.path.join("data/ACME_Demo_Data/tmp", f"{product_ID}.pickle"))

        experiment_names.append(product_ID)

    data['experiment_names'] = experiment_names
    return data, alerts



