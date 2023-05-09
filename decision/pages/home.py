import dash
import shutil
import os
import logging

from dash  import dcc
from dash  import html
from dash  import callback
from dash  import Input
from dash  import Output

import dash_bootstrap_components as dbc

dash.register_page(__name__, title="Home", path='/')

layout = html.Div([

    html.Div(children=[
        html.H1("Home"),

        # TODO - figure out better solution to this. These 8 ids are pre-declarations of ids used on the optimizer
        #           page.  Since the metrics-store is updated here, this triggers the optimizer page callback, which
        #           has metrics-store as an input.  This causes a callback warning, since these ids haven't been declared
        #           yet.  Pre-declaring them here to avoid the callback warning.  Seems to be a common Dash issue.
        html.P(id='max_iterations'),
        html.P(id='max_function_evaluations'),
        html.P(id='population_size'), 
        html.P(id='mutation_rate'),
        html.P(id='crossover_rate'),
        html.P(id='replacement_size'),
        html.P(id='replacement_type'),
        html.Div(id='runtime_bar', style={'display': 'none'}),

        html.Div(
            className="about",
            children=[
                html.H3('The onboard capability to analyze science instrument data to… Recognize Science Targets Inform Instrument Health Monitoring Discover Anomalies Create Summarizations of Observations Prioritize Data Products', className="about--about-text")
        ]),

        dbc.Row(
            [
                dbc.Col(children=[

                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.H3("Select a Configuration", style={'textAlign': 'center'}),
                    dcc.Dropdown(["ACME", "AEGIS"], 'ACME', id='config-dropdown'),

                ]),
                dbc.Col(html.Div()),
                dbc.Col(html.Div()),
            ],

        )

    ], style={'padding': 10, 'flex': 2}),


], style={'display': 'flex', 'flex-direction': 'row'})


@callback([Output('config-store', 'data')
          ],[
           Input("config-dropdown", "value"),
          ]
)
def config_dropdown_callback(config):

    if config == "ACME":
        config_path = "configs/ACME.yaml"
    elif config == "AEGIS":
        config_path = "configs/AEGIS.yaml"
    else:
        config_path = None
        logging.error(f"Unrecognized config: {config}")

    data = {'config_name':config, 'config_path':config_path}

    return [data]






