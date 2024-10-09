import dash
import shutil
import os
import logging
from zipfile import ZipFile
import base64
import io
import time
import yaml
import json

from dash  import dcc
from dash  import html
from dash  import callback
from dash  import Input
from dash  import Output
from dash  import State
from dash.exceptions import PreventUpdate


import dash_bootstrap_components as dbc

layout = html.Div([

    html.Div(children=[
        html.H3("Data-Driven Efficient Configuration of Instruments"),
        html.H3("by Scientific Intent for Operational Needs"),

        dcc.Store(id='button_memory'),
        
        html.Div(
            className="about",
            children=[
                html.P('The onboard capability to analyze science instrument data to…', className="about-text"),
                html.P('Recognize Science Targets Inform Instrument Health Monitoring Discover Anomalies', className="about-text"),
                html.P('Create Summarizations of Observations Prioritize Data Products', className="about-text")
        ]),

        dbc.Row(
            [
                dbc.Col(children=[
                    html.H3("Select a Task", style={'textAlign': 'center'}),
                    dcc.Dropdown(["AEGIS", "ACME"], 'AEGIS', id='config-dropdown'),

                ]),
                dbc.Col(html.Div(children = [
                    html.H3("Start with a previous run", style={'textAlign': 'center'}),
                    html.P("Select the task on the left and then upload the run zip file", style={'textAlign': 'center', 'fontSize': "16px"}),
                    dcc.Upload(id = "upload-run", children=[dcc.Loading(children = [html.Div([
                        html.H5('Drop Run Zip File', className = "drop-title"), html.Span("or", style = {'margin-bottom': '0.5rem'}), 
                        dbc.Button("Select Zip File", outline=False, color="primary", size='sm', className = "drop-button")
                    ], id = "center-drop-container")], id = "drop-loading")], className = "drop-container", accept=".zip", className_active="drop-container-active")
                ])),
                
            ], style = {'margin': 0, "padding-top": "50px"}

        )

    ], className = "home-container"),


], className = "")


@callback(Output('config-store', 'data')
          ,[
           Input("config-dropdown", "value"),
           Input("upload-store", 'data')
          ]
)
def config_dropdown_callback(config, upload_store):
    if upload_store:
        return {'config_name':upload_store['config_name'], 'config_path': upload_store['config_path']}

    if config == "ACME":
        config_path = "configs/ACME.yaml"
    elif config == "AEGIS":
        config_path = "configs/AEGIS.yaml"
    else:
        config_path = None
        logging.error(f"Unrecognized config: {config}")

    data = {'config_name':config, 'config_path':config_path}
    return data

@callback([Output('upload-store', 'data'),
           Output('upload-run', 'style'),
           Output('drop-loading', 'children'),
           Output('cart-store-loader', 'data', allow_duplicate=True),
           Output('plot-store', 'data', allow_duplicate=True),
           Output('test-image-store', 'data', allow_duplicate=True)],
           Output('pareto-table', 'selected_rows', allow_duplicate=True),
           Output('run-datetime-store', 'data', allow_duplicate=True),
           Input('upload-run', 'contents'),
           State('upload-run', 'filename'),
           prevent_initial_call=True
)
def upload_callback(list_of_contents, list_of_names):
    
    if list_of_contents is None:
        raise PreventUpdate
    # only use the first uploaded zip file
    content = list_of_contents
    zip_name = list_of_names

    if(os.path.exists(f"./runs/{zip_name[:-4]}")):
        shutil.rmtree(f"./runs/{zip_name[:-4]}", ignore_errors=True)

    content_type, content_string = content.split(',')
    content_decoded = base64.b64decode(content_string)
    zip_str = io.BytesIO(content_decoded)
    with ZipFile(zip_str) as zip_file:
        zip_file.extractall(f"./runs/{zip_name[:-4]}/")

    with open(f"./runs/{zip_name[:-4]}/run_config.yaml", 'r') as f:
        run_config = yaml.safe_load(f)

    with open(f"./runs/{zip_name[:-4]}/ui_status.json", 'r') as f:
        ui_status = json.load(f)

    run_config = {k: v for d in run_config if type(d) is dict for k, v in d.items() }

    run_datetime = zip_name[:-4]
    
    if(f"./runs/{run_datetime}" != f"./runs/{run_config['run_datetime']}"):
        if(os.path.exists(f"./runs/{run_config['run_datetime']}")):
            shutil.rmtree(f"./runs/{run_config['run_datetime']}", ignore_errors=True)
        shutil.move(f"./runs/{run_datetime}", f"./runs/{run_config['run_datetime']}")

    uploaded_text = html.H3("Uploaded")
    drop_files_style = {"border-style": "solid", "border-color": "#28a745"}

    ui_status['cart-store']['loaded'] = False
    ui_status['cart-store']['metrics'] = []
    
    return run_config, drop_files_style, uploaded_text, ui_status.get("cart-store", {'configs': [], 'loaded': False, 'metrics': []}), ui_status.get("plot-store", {}), ui_status.get("test-image-store", {}), ui_status.get("cart-store", []).get("configs", []), run_datetime






