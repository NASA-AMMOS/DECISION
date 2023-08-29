import dash
import time
import subprocess
import psutil
import traceback
import os
import signal
import logging
import jinja2

from dash            import dcc
from dash            import html
from dash            import callback
from dash            import Input
from dash            import Output
from dash            import State
from dash.exceptions import PreventUpdate

import numpy                     as np
import plotly.express            as px
import pandas                    as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects      as go

dash.register_page(__name__, title="Optimizer")

layout = html.Div([

    dcc.Store(id='start_button_memory'),

    # TODO - figure out better solution to this. These 5 ids are pre-declarations of ids used on the optimizer
    #           page.  Since the metrics-store is updated here, this triggers the optimizer page callback, which
    #           has metrics-store as an input.  This causes a callback warning, since these ids haven't been declared
    #           yet.  Pre-declaring them here to avoid the callback warning.  Seems to be a common Dash issue.
    html.Div(id='pareto-graph', style= {'display': 'none'}),
    html.Div(id='cluster-table', style= {'display': 'none'}),
    html.Div(id='dropdown_col_1', style= {'display': 'none'}),
    html.Div(id='dropdown_col_2', style= {'display': 'none'}),
    html.Div(id='runtime_bar', style={'display': 'none'}),

    dbc.Row(
        [
            dbc.Col(children=[
                dbc.Row(children=[
                    html.H1("Genetic Algorithm Configuration"),
                    html.Br(),
                    html.Br(),
                    html.H5("Maximum Iterations"),
                    dcc.Slider(0, 1000000, 100, value=300000, marks={0:'0',1000000:'1000000'}, tooltip={"placement": "bottom", "always_visible": True}, id='max_iterations'),
                    html.Br(),
                    html.Br(),
                    html.H5("Maximum Function Evaluations"),
                    dcc.Slider(0, 1000000, 100, value=300000, marks={0:'0',1000000:'1000000'}, tooltip={"placement": "bottom", "always_visible": True}, id='max_function_evaluations'),
                    html.Br(),
                    html.Br(),
                    html.H5("Population Size"),
                    dcc.Slider(0, 500, 1, value=50, marks={0:'0',500:'500'}, tooltip={"placement": "bottom", "always_visible": True}, id='population_size'),
                    html.Br(),
                    html.Br(),
                    html.H5("Mutation Rate"),
                    dcc.Slider(0, 1.0, 0.1, value=1.0, marks={0:'0',1.0:'1.0'}, tooltip={"placement": "bottom", "always_visible": True}, id='mutation_rate'),
                    html.Br(),
                    html.Br(),
                    html.H5("Crossover Rate"),
                    dcc.Slider(0, 1.0, 0.1, value=0.0, marks={0:'0',1.0:'1.0'}, tooltip={"placement": "bottom", "always_visible": True}, id='crossover_rate'),
                    html.Br(),
                    html.Br(),
                    html.H5("Replacement Size"),
                    dcc.Slider(0, 100, 1, value=10, marks={0:'0',100:'100'}, tooltip={"placement": "bottom", "always_visible": True}, id='replacement_size'),
                    html.Br(),
                    html.Br(),
                    html.H5("Replacement Type"),
                    dcc.RadioItems(['Elitist', 'CHC','Random'], 'Elitist', labelStyle={'display': 'block'}, id='replacement_type'),
                    dbc.Button("Run", outline=True, color="success", className="run", size='sm', id='start_button', style={"margin-bottom": "10px", "margin-top": "20px"}),
                    dbc.Button("Stop", outline=True, color="danger", className="stop", size='sm', id='stop_button'),
                ]),

                html.Br(),
                html.H3("System Notifications"),
                html.Br(),
                html.Div(id='optimizer-alerts'),
            ]),

            dbc.Col(children=[
                dbc.Row(children=[
                    dcc.Loading(id="loading-icon",
                                type="default",
                                children=[html.Div(id='dakota-status'),
                                          html.Div(id='plots')
                                          ]),
                    dcc.Interval(id='interval-component',
                                 interval=5*1000, # in milliseconds
                                 n_intervals=0)
                ])
            ])
        ],
    ),

    html.P(id='placeholderStopButton'),


], style={'display': 'flex', 'flex-direction': 'row'})


@callback(Output('optimizer-store', 'data'),
          Input('max_iterations', 'value'),
          Input('max_function_evaluations', 'value'),
          Input('population_size', 'value'),
          Input('mutation_rate', 'value'),
          Input('crossover_rate', 'value'),
          Input('replacement_size', 'value'),
          Input('replacement_type', 'value'),
          Input('parameters-store', 'data'),
          Input('metrics-store', 'data'),
          prevent_initial_call=True,
)
def callbackSliders(max_iterations,
                    max_function_evaluations,
                    population_size,
                    mutation_rate,
                    crossover_rate,
                    replacement_size,
                    replacement_type,
                    parameters_store,
                    metrics_store):

    if parameters_store['parameters'] == []:
        raise PreventUpdate

    if replacement_type is None:
        raise PreventUpdate

    metric_names = metrics_store['metrics']
    metric_names = [x.replace(" ","_") for x in metric_names]
    metric_names = [f"                '{x}'" for x in metric_names]
    metric_names[0] = metric_names[0].replace("                ", "  descriptors = ")
    metric_names = "\n".join(metric_names)

    metric_types = metrics_store['metrics']
    metric_types = [metric.split(" ")[0][:3].lower() for metric in metric_types]
    metric_types = [f"          '{x}'" for x in metric_types]
    metric_types[0] = metric_types[0].replace("          ", "  sense = ")
    metric_types = "\n".join(metric_types)

    metrics_count = len(metrics_store['metrics'])

    continuous_variable_lower_bounds = f"  lower_bounds         {parameters_store['parameters'][4][0]}           {parameters_store['parameters'][5][0]}"
    continuous_variable_upper_bounds = f"  upper_bounds         {parameters_store['parameters'][4][1]}            {parameters_store['parameters'][5][1]}  "

    discrete_variable_lower_bounds = f"  lower_bounds         {parameters_store['parameters'][0][0]}           {parameters_store['parameters'][1][0]}            {parameters_store['parameters'][2][0]}            {parameters_store['parameters'][3][0]}            {parameters_store['parameters'][6][0]}            {parameters_store['parameters'][7][0]}            {parameters_store['parameters'][8][0]}"
    discrete_variable_upper_bounds = f"  upper_bounds         {parameters_store['parameters'][0][1]}            {parameters_store['parameters'][1][1]}           {parameters_store['parameters'][2][1]}            {parameters_store['parameters'][3][1]}            {parameters_store['parameters'][6][1]}            {parameters_store['parameters'][7][1]}            {parameters_store['parameters'][8][1]}"

    update_dict = {"max_iterations":max_iterations,
                   "max_function_evaluations": max_function_evaluations,
                   "population_size": population_size,
                   "mutation_rate": mutation_rate,
                   "crossover_rate": crossover_rate,
                   "replacement_type": replacement_type.lower(),
                   "replacement_size": replacement_size,
                   "continuous_variable_count": 2,
                   "discrete_variable_count": 7,
                   "metrics_count": metrics_count,
                   "metric_names": metric_names,
                   "optimization_type": metric_types,
                   "continuous_variable_descriptors": "  descriptors       'sigma'   'sigma_ratio'",
                   "discrete_variable_descriptors": "  descriptors      'center_x'     'window_x'    'window_y'    'denoise_x'    'min_filtered_threshold'   'min_SNR_conv'   'min_peak_volume'",
                   "continuous_variable_lower_bounds":continuous_variable_lower_bounds,
                   "continuous_variable_upper_bounds": continuous_variable_upper_bounds,
                   "discrete_variable_lower_bounds": discrete_variable_lower_bounds,
                   "discrete_variable_upper_bounds": discrete_variable_upper_bounds}

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = 'dakota.template'
    template = template_env.get_template(html_template)
    output_text = template.render(update_dict)

    text_file = open('dakota.input', "w")
    text_file.write(output_text)
    text_file.close()

    logging.info("Optimizer store updated")
    return ''


@callback(Output('start_button_memory', 'data'),
          Input('start_button', 'n_clicks'),
         [State('start_button_memory', 'data')]
)
def callbackButton(n_clicks, data):

    if n_clicks is None:
        raise PreventUpdate

    if n_clicks == 1:
        # Run Dakota (hard coded demo for now)
        logging.info("Lanching Dakota")
        if 'DAKOTA_ENGINE' not in os.environ or os.environ['DAKOTA_ENGINE'] == "local":
            dakota_process = subprocess.Popen(["dakota", "-i", "dakota.input", "-o", "dakota.out", ">", "dakota.stout"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Dakota running with PID: {dakota_process.pid}")
        elif os.environ['DAKOTA_ENGINE'] == "docker":
            dakota_process = subprocess.Popen(["docker", "run", "dakota", "-i", "dakota.input", "-o", "dakota.out"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Dakota running with PID: {dakota_process.pid}")
        elif os.environ['DAKOTA_ENGINE'] == 'ecs':
            None

    data = data or {'clicks': 0}
    data['clicks'] = data['clicks'] + 1

    return data

@callback([Output('plots', 'children'),
           Output('dakota-status', 'children'),
           Output('pareto-store', 'data')],
          [Input('start_button_memory', 'modified_timestamp'),
          Input('metrics-store', 'data')],
          Input('interval-component', 'n_intervals'))
def on_data(ts, store, n):

    metrics = store['metrics']
    metrics = [i.replace(" ","_") for i in metrics]

    i = 0
    metrics_dict = {}
    dynamic_plots = []
    dakota_status = []
    dakota_status_text = ""

    if ts is None:
        return dynamic_plots, dakota_status, metrics_dict

    try:

        process = subprocess.Popen(['pgrep', '-f', 'dakota'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(len(out) == 0):
            dakota_running = "Stopped"
        else:
            dakota_running = "Running"

        with open("dakota.out") as file:
            lines = [line.rstrip() for line in file]

            split_index = [idx for idx, s in enumerate(lines) if 'End DAKOTA input file' in s][0]

            input_list = lines[:split_index]
            output_list = lines[split_index:]

            for metric in metrics:
                metrics_dict[metric] = [i for i in output_list if metric in i]
                metrics_dict[metric] = [float(i.lstrip().split(" ")[0]) for i in metrics_dict[metric]]

        for x in range(0, len(store['metrics'])):
            y = metrics_dict[metrics[x]]
            fig = px.scatter(x=np.arange(0, len(y)), y=y, title="Automatic")
            fig.update_layout(xaxis_title="Iteration", title={'text': store["metrics"][x],'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top'})
            fig.write_image(f"plots/metric_{x}.png")
            dynamic_plots.append(dcc.Graph(id='metrics-graph'+str(i),figure=fig))
            i = i + 1

        time.sleep(1)
        dakota_status_text = f"Dakota Status: {dakota_running} (Iteration: {len(y)})"

    except:
        dakota_status_text = f"Dakota Status: Initializing..."

    dakota_status.append(html.H1(dakota_status_text, style={'textAlign': 'center'}))
    return html.Div(dynamic_plots), dakota_status, metrics_dict


@callback(Output('placeholderStopButton', 'children'),
          Input('stop_button', 'n_clicks')
)
def dakota_shutdown(button_press):

    if button_press is None:
        raise PreventUpdate

    logging.info("Attempting to shut down Dakota")
    process = subprocess.Popen(['pkill', '-9', '-f', 'dakota'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    logging.info(f"Kill log: {out}")

    return ''





