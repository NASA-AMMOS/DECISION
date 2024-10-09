import dash
import os
import yaml
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

layout = html.Div([html.Div([

    html.Div(
        className="db-header",
        children=[
            dbc.Col(width=11, children=[
                html.Div(children=[
                    html.H3("Select Experiments To Optimize With"),
                ], style={"float": "left"}),
            ]),
            dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Experiments to Optimize With"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                    ]),
                ]),
    ], style={ 'flex': 1, }),

    html.Div(id = "table-container", children=[dash_table.DataTable(id="table",)], style={ 'flex': 1,}),  
    html.Div(
        children=[
            dbc.Button("Select All Experiments", size='sm', id='select-all-button', style={"margin-right": "5px"}),
            dbc.Button("Deselect All Experiments", size='sm', id='deselect-all-button'),
        ], className="database-buttons"),

], className = "database-container")])

@callback(
    Output('table-container', 'children'),
    Input('config-store', 'data')
)
def update_table(config_store):
    config_name = config_store["config_name"]
    
    df = pd.read_csv(f"./data/{config_name}_Demo_Data/experiments.csv")

    return [
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            row_selectable="multi",
            row_deletable=False,
            editable=False,
            selected_rows = [0],
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "scroll"},
            style_cell={'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 10,
                        'textAlign': 'center',
                        'whiteSpace': 'normal'
            })
    ]

@callback(
        Output('table', 'selected_rows'),[
        Input('select-all-button', 'n_clicks'),
        Input('deselect-all-button', 'n_clicks'),
        Input('upload-store', 'data')
    ],[
        State('table', 'data'),
        State('table', 'derived_virtual_data'),
        State('table', 'derived_virtual_selected_rows')
    ]
)
def select_all(select_n_clicks, deselect_n_clicks, upload_store, original_rows, filtered_rows, selected_rows):
    
    if upload_store:
        return upload_store['experiments']
    
    ctx = dash.callback_context.triggered[0]
    ctx_caller = ctx['prop_id']
    if filtered_rows is not None:
        if ctx_caller == 'select-all-button.n_clicks':
            selected_ids = [row for row in filtered_rows]
            return [i for i, row in enumerate(original_rows) if row in selected_ids]
        if ctx_caller == 'deselect-all-button.n_clicks':
            return []
        raise PreventUpdate
    else:
        raise PreventUpdate


@callback(
        Output('experiments-store', 'data'),
    [
        Input('table', 'derived_virtual_selected_rows'),
        Input('upload-store', 'data')
    ],
    [
        State('table', 'data'),
        State('config-store', 'data')
    ]

)
def callbackExperimentStoreUpdate(selected_experiments, upload_store, table_data, config_store):
    config_path = config_store['config_path']
    config_name = config_store['config_name']

    with open(config_path) as f:
        config = yaml.safe_load(f)

    experiments = upload_store.get("experiments", [])
    if selected_experiments is not None and selected_experiments != []:
        experiments.extend([experiment for experiment in selected_experiments if experiment not in experiments])

    data = {"experiments": experiments}

    # make a copy of each selected observation in tmp directory for processing
    for x in range(0, len(experiments)):
        product_ID = table_data[x]['ID']

        for key in table_data[x]:
            if key not in data:
                data[key] = []
            data[key].append(table_data[x][key])

        if not os.path.exists(f"data/{config_name}_Demo_Data/tmp"):
            os.mkdir(f"data/{config_name}_Demo_Data/tmp")

        # TODO - put in config during generalization activity
        shutil.copy(os.path.join(f"data/{config_name}_Demo_Data/{config['data']['data_extension']}s",f"{product_ID}.{config['data']['data_extension']}"),os.path.join(f"data/{config_name}_Demo_Data/tmp", f"{product_ID}.{config['data']['data_extension']}"))

    return data