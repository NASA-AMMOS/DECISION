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
from dash            import ctx

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

layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.Div(children=[
                html.Div(id='seed_div'),
                # Parameters panel
                html.Div(className="metrics-column-left", children=[
                    html.Div(className="content-header",
                        children=[
                            dbc.Row(children=[
                                dbc.Col(width=11, children=[
                                    html.H1("Parameter Optimization")
                                    ]),
                                dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                                    html.Button(id={"type":'modal-button', "name":"Parameter Optimization"}, className="modal-button", children=[
                                        html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                                        ]),
                                    ]),
                            ]),
                    ]),
                    html.Div(id='sliders'),        
                    html.Br(),
                    html.Br(),
                ]),
            ]),
        ),
        dbc.Col(
            html.Div(children=[
                html.Div(className='metrics-column-right', children=[
                    html.Div(className="content-header",
                            children=[
                                dbc.Row(children=[
                                    dbc.Col(width=11, children=[
                                        html.H1("Metrics to Optimize")
                                        ]),
                                    dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                                        html.Button(id={"type":'modal-button', "name":"Metrics to Optimize"}, className="modal-button", children=[
                                            html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                                            ]),
                                        ]),
                                ]),
                    ]),
                    html.Div(className='content-box', children=[
                        html.Div(className="metrics-explanation", children=[
                            html.H3("Optimization Metrics"),
                            html.P("Choose at least two metrics to optimize over."),
                        ]),

                        html.Div(
                            className='optimization-checklist',
                            children=[
                                html.Div(id='checklist-container', children = [dcc.Checklist(id = "checklist")])
                        ]),

                        html.Div(className="metrics-explanation", children=[
                            html.H3("Runtime Estimate"),
                            html.P("The percent of the maximum parameter search space which estimates the runtime of the parameter optimization."),
                        ]),
                        html.Div(className='runtime-est', id='runtime_bar', style={ 'flex': 1}),

                    ]),
                ])
            ])
        ),
    ]),
], className = "")


@callback([Output('runtime_bar', 'children'),
           Output('parameters-store', 'data')
          ],[
           Input({"type": "parameter-slider", "index": ALL}, "value"),
           Input('config-store', 'data'),
           Input('upload-store', 'data')
          ],
)
def update_runtime_estimate(slider_values, config_store, upload_store):
    
    if upload_store:
        slider_values = upload_store["parameters"]
    elif slider_values == []:
        raise PreventUpdate
    
    param_max_ranges = get_param_max_ranges(config_store['config_path'])
    
    if len(slider_values) != len(param_max_ranges):
        raise PreventUpdate
    
    step_types, names = get_param_info(config_store)

    runtime_bar = []

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

    parameters_store = {}
    
    parameters_store['parameters'] = slider_values

    parameters_store['step_types'] = step_types

    parameters_store['names'] = names

    runtime_component = html.Div(className = "row-display", children = [html.Span("Low", style = {"padding": "0 10px"}), dbc.Progress(runtime_bar, style = {"width": "100%"}), html.Span("High", style = {"padding": "0 10px"})])

    return [runtime_component], parameters_store

def get_param_info(config_store):
    step_types = []
    names = []

    with open(config_store['config_path']) as f:
        config = yaml.safe_load(f)
        num_blocks = len(config['parameters'])

    for x in range(0,num_blocks):
        params = config['parameters'][x]['parameters']
        for y in range(0, len(params)):
            if(params[y]['type'] == 'range'):
                step = params[y]['step']
                if type(step) == float:
                    step_types.append("continuous")
                else:
                    step_types.append("discrete")
                if "variable_name" in params[y]:
                    names.append(params[y]['variable_name'])
                else:
                    names.append(params[y]['name'].lower().replace(" ", "_"))
    return step_types, names


@callback([Output('sliders', 'children'),
           Output('checklist-container', 'children'),
           Output('modal-store', 'data'),
          ],[
           Input("seed_div", "children"),
           Input('config-store', 'data'),
           Input('upload-store', 'data')
          ],
          State('modal-store', 'data'),
          prevent_initial_call=True,
)
def initial_callback(metrics, config_store, upload_store, modal_store):
    slider_values = []
    if upload_store:
        slider_values = upload_store["parameters"]
        slider_values = [v for x in slider_values for v in x]
    
    blocks = []

    with open(config_store['config_path']) as f:
        config = yaml.safe_load(f)
        num_blocks = len(config['parameters'])
        default_metrics = config['metrics']['default']
        all_metrics = config['metrics']['all']

    index = 0

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
            param_name = params[y]['name']
            param_description = params[y]['description']

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

            if 'modal_description' in params[y]:
                modal_store[param_name] = params[y]['modal_description']

                text_block_1.append(
                    dbc.Row([
                        dbc.Col(width=10, children=[
                            html.H5(f"{param_name}", className="metrics-header")
                        ]),
                        dbc.Col(width=2, style={"align-content": "center"}, children=[
                        html.Button(id={"type":'modal-button', "name":param_name}, className="modal-button", children=[
                            html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                            ]),
                        ])
                    ]),
                )
            else:
                text_block_1.append(html.H5(f"{param_name}", className="metrics-header"))

            text_block_1.append(html.P(f"{param_description}"))

            if not slider_values:
                slider_block_1.append(dcc.RangeSlider(min_range, max_range, step, value=[min_default,max_default], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":index}))
            else:
                slider_block_1.append(dcc.RangeSlider(min_range, max_range, step, value=[slider_values.pop(0),slider_values.pop(0)], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":index}))

            text_block_2 = []
            slider_block_2 = []

            if remaining_sliders != 1:
                step = params[y+1]['step']
                param_type = params[y+1]['type']
                param_name = params[y+1]['name']
                param_description = params[y+1]['description']
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

                if 'modal_description' in params[y+1]:
                    modal_store[param_name] = params[y+1]['modal_description']

                    text_block_2.append(
                        dbc.Row([
                            dbc.Col(width=10, children=[
                                html.H5(f"{param_name}", className="metrics-header")
                            ]),
                            dbc.Col(width=2, style={"align-content": "center"}, children=[
                            html.Button(id={"type":'modal-button', "name":param_name}, className="modal-button", children=[
                                html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                                ]),
                            ])
                        ]),
                    )
                else:
                    text_block_2.append(html.H5(f"{param_name}", className="metrics-header"))

                text_block_2.append(html.P(f"{params[y+1]['description']}"))


                if not slider_values:
                    slider_block_2.append(dcc.RangeSlider(min_range, max_range, step, value=[min_default,max_default], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":index + 1}))
                else:
                    slider_block_2.append(dcc.RangeSlider(min_range, max_range, step, value=[slider_values.pop(0),slider_values.pop(0)], marks={min_range:min_range_text,max_range:max_range_text}, tooltip={"placement": "bottom", "always_visible": True}, id={"type":'parameter-slider', "index":index + 1}))

                
            sliders.append(html.Div(className = "metrics-row", children=[
                html.Div(className='six-columns', children=text_block_1, style={'width':'70%',"margin-right": "50px"}),
                html.Div(className='six-columns', children=text_block_2, style={'width':'70%'})])
            )

            sliders.append(html.Div(children=[
                html.Div(className='', children=slider_block_1, style={'width':'70%',"margin-right": "50px"}),
                html.Div(className='', children=slider_block_2, style={'width':'70%'})
            ], style=dict(display='flex')))

            index = index + 2
        if 'modal_description' in config['parameters'][x]:
            modal_store[block_name] = config['parameters'][x]['modal_description']

            blocks.append(html.Div(className="content-box",children=[html.Div(className="metrics-explanation",children=[
                dbc.Row([
                    dbc.Col(width=11, children=[
                        html.H3(f"{block_name}")
                    ]),
                    dbc.Col(width=1, style={"align-content": "center"},  children=[
                        html.Button(id={"type":'modal-button', "name":block_name}, className="modal-button", children=[
                            html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                        ]),
                    ])
                ]),
                html.P(f"{block_description}"),
                ]),
                html.Div(children=sliders, style={'padding': "0 10px", 'flex': 1}),
            ]))
        else:
            blocks.append(html.Div(className="content-box",children=[html.Div(className="metrics-explanation",children=[
                dbc.Row([
                    dbc.Col(width=12, children=[
                        html.H3(f"{block_name}")
                    ]),
                ]),
                html.P(f"{block_description}"),
                ]),
                html.Div(children=sliders, style={'padding': "0 10px", 'flex': 1}),
            ]))

    metrics_list = [{"label": html.Span(metric, className = "metric-span"), "value": metric} for metric in all_metrics]

    if upload_store:
        metrics_checklist = dcc.Checklist(metrics_list,upload_store["metrics"],id='checklist',labelStyle={'display': 'block'})
    else:
        metrics_checklist = dcc.Checklist(metrics_list,default_metrics,id='checklist',labelStyle={'display': 'block'})

    return html.Div(blocks), metrics_checklist, modal_store


@callback(
    Output('metrics-store', 'data'),
    Input("checklist", "value"),
)
def callback(metrics):

    if metrics is None:
        raise PreventUpdate
    data = {'metrics':metrics}

    return data