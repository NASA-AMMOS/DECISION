import dash
import yaml

from dash            import Dash
from dash            import html
from dash            import Input
from dash            import Output
from dash            import dcc
from dash            import callback
from dash            import State
from dash            import ALL
from dash.exceptions import PreventUpdate

import dash_daq                  as daq
import numpy                     as np
import dash_bootstrap_components as dbc

def get_param_max_ranges(config_path):

    param_ranges = []
    with open(config_path) as f:
        config = yaml.safe_load(f)
        num_blocks = len(config['parameters'])

    for x in range(0,num_blocks):
        params = config['parameters'][x]['parameters']

        for y in range(0, len(params)):
            min_range = params[y]['min_range']
            max_range = params[y]['max_range']

            param_ranges.append([min_range,max_range])

    return param_ranges


dash.register_page(__name__, title="Metrics")

layout = html.Div([

    dbc.Row([
        dbc.Col(
            html.Div
            (children=[

            html.Br(),
            html.Br(),

            # TODO - figure out better solution to this. These 16 ids are pre-declarations of ids used on the optimizer
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

            html.Div(id='seed_div'),

            # Parameters panel
            html.Div(
                className="metrics-column",
                children=
                [
                    html.Div(id='sliders'),        
                    html.Br(),
                    html.Br(),
                ]),
            ]),

            ),
        dbc.Col(html.Div(
            className='optimization-column',
            children=[
            html.Div(children=[

                html.H3("Optimization Metrics"),
                
            html.Div(
            className='optimization-checklist',
            children=[
                html.Div(id='checklist')
            ]),

                html.Br(),
                html.Br(),
                html.H3("Runtime Estimate"),
                html.Br(),

                html.Div(className='runtime-est', id='runtime_bar', style={'padding': 10, 'flex': 1}),

                html.Br(),
                html.Br(),
                html.H3("System Notifications"),
                html.Br(),

            ], style={'padding': 10, 'flex': 1}),

            html.Div( id='alerts', style={'padding': 10, 'flex': 1})

        ])),
    ]),
])


@callback([Output('runtime_bar', 'children'),
           Output('parameters-store', 'data')
          ],[
           Input({"type": "parameter-slider", "index": ALL}, "value"),
           Input('config-store', 'data')
          ],
          prevent_initial_call=True,
)
def update_runtime_estimate(slider_values, config_store):

    if slider_values == []:
        raise PreventUpdate

    runtime_bar = []

    param_max_ranges = get_param_max_ranges(config_store['config_path'])

    slider_ratios = []
    num_sliders = len(slider_values)
    for x in range(0, num_sliders):
        if slider_values[x][0] != slider_values[x][1]:
            ratio = (slider_values[x][1]-slider_values[x][0])/(param_max_ranges[x][1]-param_max_ranges[x][0])
            slider_ratios.append(ratio)

    combined_ratio = np.average(slider_ratios)

    if combined_ratio <= .333:
        runtime_bar.append(dbc.Progress(value=(combined_ratio*100), color="success", bar=True))
    elif combined_ratio > .333 and combined_ratio <= .666:
        runtime_bar.append(dbc.Progress(value=33.3, color="success", bar=True))
        runtime_bar.append(dbc.Progress(value=((combined_ratio-.333)*100), color="warning", bar=True))
    else:
        runtime_bar.append(dbc.Progress(value=33.3, color="success", bar=True))
        runtime_bar.append(dbc.Progress(value=33.3, color="warning", bar=True))
        runtime_bar.append(dbc.Progress(value=((combined_ratio-.666)*100), color="danger", bar=True))

    data = {'parameters':slider_values}

    return [dbc.Progress(runtime_bar)], data

@callback([Output('sliders', 'children'),
           Output('checklist', 'children')
          ],[
           Input("seed_div", "children"),
           Input('config-store', 'data')
          ]
)
def initial_callback(metrics, config_store):

    blocks = []

    with open(config_store['config_path']) as f:
        config = yaml.safe_load(f)
        num_blocks = len(config['parameters'])
        default_metrics = config['metrics']['default']
        all_metrics = config['metrics']['all']

    for x in range(0,num_blocks):
        sliders = []
        params = config['parameters'][x]['parameters']
        block_name = config['parameters'][x]['name']
        block_description = config['parameters'][x]['description']

        for y in range(0, len(params), 2):

                remaining_sliders = len(params)-y

                text_block_1 = []
                slider_block_1 = []

                step = params[y]['step']
                param_type = params[y]['type']
                if type(step) == float:
                    min_range = float(params[y]['min_range'])
                    max_range = float(params[y]['max_range'])
                    min_default = float(params[y]['min_default'])
                    max_default = float(params[y]['max_default'])
                else:
                    min_range = params[y]['min_range']
                    max_range = params[y]['max_range']
                    min_default = params[y]['min_default']
                    max_default = params[y]['max_default']

                if param_type == "constant":
                    min_range_text = 'constant'
                    max_range_text = 'constant'
                else:
                    min_range_text = str(params[y]['min_range'])
                    max_range_text = str(params[y]['max_range'])

                text_block_1.append(html.H5(f"{params[y]['name']} - {params[y]['description']}"))
                text_block_1.append(html.Br())
                slider_block_1.append(dcc.RangeSlider(min_range, max_range, step, value=[min_default,max_default], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":1}))

                text_block_2 = []
                slider_block_2 = []

                if remaining_sliders != 1: 
                    step = params[y+1]['step']
                    param_type = params[y+1]['type']
                    if type(step) == float:
                        min_range = float(params[y+1]['min_range'])
                        max_range = float(params[y+1]['max_range'])
                        min_default = float(params[y+1]['min_default'])
                        max_default = float(params[y+1]['max_default'])
                    else:
                        min_range = params[y+1]['min_range']
                        max_range = params[y+1]['max_range']
                        min_default = params[y+1]['min_default']
                        max_default = params[y+1]['max_default']

                    if param_type == "constant":
                        min_range_text = 'constant'
                        max_range_text = 'constant'
                    else:
                        min_range_text = str(params[y+1]['min_range'])
                        max_range_text = str(params[y+1]['max_range'])

                    text_block_2.append(html.H5(f"{params[y+1]['name']} - {params[y+1]['description']}"))
                    slider_block_2.append(dcc.RangeSlider(min_range, max_range, step, value=[min_default,max_default], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":1}))
                text_block_2.append(html.Br())

                sliders.append(html.Div(children=[
                    html.Div(className='six columns', children=text_block_1, style={'width':'70%',"margin-right": "50px"}), 
                    html.Div(className='six columns', children=text_block_2, style={'width':'70%'})], style=dict(display='flex'))
                )

                sliders.append(html.Div(children=[
                    html.Div(className='six columns', children=slider_block_1, style={'width':'70%',"margin-right": "50px"}), 
                    html.Div(className='six columns', children=slider_block_2, style={'width':'70%'})
                ], style=dict(display='flex')))

        blocks.append(html.Div(className="metrics-sliders",children=[html.Div(className="metrics-explanation",children=[
            html.H4(f"{block_name}"),
            html.H6(f"{block_description}"), 
            html.Br()]),
            html.Div(children=sliders, style={'padding': 10, 'flex': 1,'flex-direction': 'col'}),
        ]))

    metrics_list = dcc.Checklist(all_metrics,default_metrics,id='checklist',labelStyle={'display': 'block'})
    
    return html.Div(blocks), metrics_list


@callback([Output('metrics-store', 'data'),
           Output('alerts', 'children'),
          ],[
           Input("checklist", "value"),
          ]
)
def callback(metrics):

    data = {'metrics':metrics}

    # colors: success (green), warning (yellow), danger (red) 
    alerts = []

    # if metrics are not yet populated do not continue
    if metrics is None:
        raise PreventUpdate

    # if no metrics are selected, provide a danger alert
    if len(metrics) < 2:
        alerts.append(dbc.Alert("Please select at least two metrics to optimize over", color="danger"))
    
    # if 4 or more metrics are selected, prov
    if len(metrics) >= 4:
        alerts.append(dbc.Alert("Be careful adding too many metrics, this can degrade overall performance.", color="warning"))

    return data, alerts


