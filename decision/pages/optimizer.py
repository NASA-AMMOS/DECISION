import dash
import time
import subprocess
import psutil
import traceback
import os
import signal
import logging
import jinja2
import yaml
import datetime
import shutil

from dash            import dcc
from dash            import html
from dash            import callback
from dash            import Input
from dash            import Output
from dash            import State
from dash            import ALL
from dash.exceptions import PreventUpdate

import numpy                     as np
import plotly.express            as px
import pandas                    as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects      as go

# TODO - Dash currently has no mechanism for turning off an interval component.
#          Until this feature exists, we set the interval to a high value to 
#          'turn off' the interval when optimization is stopped.  This stops
#           future pages from constantly refreshing.
# in milliseconds
SHORT_INTERVAL_TIME = 5000
LONG_INTERVAL_TIME = 50000000000000000


layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.Div
            (children=[

            # Parameters panel
            html.Div(
                className="metrics-column-left",
                children=
                [
                    html.Div(className = "content-box", children = [
                        html.Div(children = [
                            html.Div(children = [
                                dbc.Col(width=11, children=[
                                    html.H3("Genetic Algorithm Configuration"),
                                ]),
                                dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                                    html.Button(id={"type":'modal-button', "name":"Genetic Algorithm Configuration"}, className="modal-button", children=[
                                        html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                                    ]),
                                ]),
                                ], style = {"padding": "25px 15px 0 15px", "display": "flex"}),
                            html.H5("Maximum Iterations", className="slider-header"),
                            html.P("Max number of population generations to create. This parameter is useful for controlling runtime. More iterations will likely improve results but translate into a longer runtime. 10-100 iterations is a good range for most optimizations.", className="slider-text"),
                            dcc.Slider(0, 1000, 1, value=10, marks={0:'0',1000:'1000'}, tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 1}),
                            html.H5("Maximum Function Evaluations", className="slider-header"),
                            html.P("Max number of individual evaluations (of the objective function on population members). Can be used as a simple stopping criterion, especially in cases where the evaluation of each population member is expensive. However, it's typical to leave this as a large value and allow the `Max Iterations` parameter to terminate the optimization instead.", className="slider-text"),
                            dcc.Slider(0, 100000, 100, value=10000, marks={0:'0',100000:'100000'}, tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 2}),
                            html.H5("Population Size", className="slider-header"),
                            html.P("Initial number of individuals in the population. Note that the population may wax/wane as the optimization iterations progress. Large values will more thoroughly test the optimization space but increase runtime.", className="slider-text"),
                            dcc.Slider(0, 1000, 1, value=50, marks={0:'0',1000:'1000'}, tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 3}),
                            html.H5("Mutation Rate", className="slider-header"),
                            html.P("Determines how likely it is for mutations to occur. Higher values will better explore the configuration space (reducing chance of getting stuck in local minima) at the risk of not annealing to the fully optimal solution.", className="slider-text"),
                            dcc.Slider(0, 1.0, 0.01, value=0.08, marks={0:'0.0',1:'1.0'}, tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 4}),
                            html.H5("Crossover Rate", className="slider-header"),
                            html.P("Determines how fast crossovers occur when combining parents information to create an offspring. Higher values will better explore the configuration space (reducing chance of getting stuck in local minima) at the cost of not annealing to the fully optimal solution.", className="slider-text"),
                            dcc.Slider(0, 1.0, 0.01, value=0.8, marks={0:'0.0',1:'1.0'}, tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 5}),
                            dbc.Button("Run", outline=False, color="primary", size='sm', id='button', style={"width": "100%", "font-size": "1.5rem", "margin-top": "30px"})
                        ], id = "optimizer-sliders", style = {"padding": "0 10px"})
                    ]),
                    
                ]),

                html.P(id='placeholderStopButton'),
            ]),

            ),
        dbc.Col(html.Div(children = [html.Div(
            id = "dakota-status",
            children=[html.Div(id='plots'),
        ]),  dcc.Interval(id='interval-component',
                                interval=SHORT_INTERVAL_TIME,
                                n_intervals=0)])),
    ]),
], className = "")


@callback(Output('optimizer-store', 'data'),
          [Input({"type": "optimizer-slider", "index": 1}, 'value'),
          Input({"type": "optimizer-slider", "index": 2}, 'value'), 
          Input({"type": "optimizer-slider", "index": 3}, 'value'), 
          Input({"type": "optimizer-slider", "index": 4}, 'value'),
          Input({"type": "optimizer-slider", "index": 5}, 'value'),
          Input('parameters-store', 'data'),
          Input('metrics-store', 'data'),
          Input('upload-store', 'data')],
          [State('machine-store', 'data'),
           State('config-store', 'data')]
)
def callbackSliders(max_iterations, 
                    max_function_evaluations, 
                    population_size, 
                    mutation_rate, 
                    crossover_rate, 
                    parameters_store,
                    metrics_store,
                    upload_store,
                    machine_store,
                    config_store):

    # TODO: Test that this actually affects the results of this function
    if upload_store:
        update_dict = upload_store["update_dict"]
    elif parameters_store['parameters'] == []:
        raise PreventUpdate
    
    metric_names = metrics_store['metrics']

    if len(metric_names) == 0:
        raise PreventUpdate
    
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

    
    continuous_variable_descriptors = '  descriptors    '
    discrete_variable_descriptors = '  descriptors    '
    continuous_variable_lower_bounds = '  lower_bounds'
    continuous_variable_upper_bounds = '  upper_bounds'
    discrete_variable_lower_bounds = '  lower_bounds'
    discrete_variable_upper_bounds = '  upper_bounds'

    continuous_variable_count = 0
    discrete_variable_count = 0
    
    for i, stype in enumerate(parameters_store["step_types"]):
        if stype == "continuous":
            continuous_variable_count = continuous_variable_count + 1
            continuous_variable_descriptors += f"   '{parameters_store['names'][i]}'"
            continuous_variable_lower_bounds += f"         {parameters_store['parameters'][i][0]}"
            continuous_variable_upper_bounds += f"         {parameters_store['parameters'][i][1]}"
        if stype == "discrete":
            discrete_variable_count = discrete_variable_count + 1
            discrete_variable_descriptors += f"   '{parameters_store['names'][i]}'"
            discrete_variable_lower_bounds += f"         {parameters_store['parameters'][i][0]}"
            discrete_variable_upper_bounds += f"         {parameters_store['parameters'][i][1]}"

    # TODO: This appears to overwrite the parameters that are uploaded via the upload-store
    update_dict = {"max_iterations":max_iterations,
                "max_function_evaluations": max_function_evaluations,
                "population_size": population_size,
                "mutation_rate": mutation_rate,
                "crossover_rate": crossover_rate,
                "continuous_variable_count": continuous_variable_count,
                "discrete_variable_count": discrete_variable_count,
                "metrics_count": metrics_count,
                "metric_names": metric_names,
                "optimization_type": metric_types,
                "continuous_variable_descriptors": continuous_variable_descriptors,
                "discrete_variable_descriptors": discrete_variable_descriptors,
                "continuous_variable_lower_bounds":continuous_variable_lower_bounds,
                "continuous_variable_upper_bounds": continuous_variable_upper_bounds,
                "discrete_variable_lower_bounds": discrete_variable_lower_bounds,
                "discrete_variable_upper_bounds": discrete_variable_upper_bounds}
    
    # Add logic to machine_store to switch between local and HPC
    template_loader = jinja2.FileSystemLoader(f'./dakota/{config_store["config_name"]}/{machine_store["machine"]}/')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = 'dakota.template'
    template = template_env.get_template(html_template)
    output_text = template.render(update_dict)
    text_file = open(f'./dakota/{config_store["config_name"]}/{machine_store["machine"]}/dakota.in', "w")
    text_file.write(output_text)
    text_file.close()
    
    logging.info("Optimizer store updated")
    return {"update_dict": update_dict}


@callback([Output('button_memory', 'data'),
           Output("run-datetime-store", 'data'),
           Output('button', 'color'),
           Output('button', 'children'),
           Output({"type": "optimizer-slider", "index": ALL}, "disabled"),
           Output({"type": "parameter-slider", "index": ALL}, "disabled"),
           Output("checklist", "options"),
           Output("table", "row_selectable"),
          ],
          [Input('button', 'n_clicks'),
           Input('upload-store', 'data')],
         [State('button_memory', 'data'),
         State('config-store', 'data'),
         State('run-datetime-store', 'data'),
         State('optimizer-store', 'data'),
         State('metrics-store', 'data'),
         State('experiments-store', 'data'),
         State('parameters-store', 'data'),
         State('machine-store', 'data')]
)
def callbackButton(n_clicks, upload_store, data, config_store, run_datetime, optimizer_store, metrics_store, experiments_store, parameters_store, machine_store):

    with open(config_store['config_path']) as f:
        config = yaml.safe_load(f)
        all_metrics = config['metrics']['all']
    
    if n_clicks is None or n_clicks == 0:
        if upload_store:
            metrics_list = [{"label": html.Span(metric, className = "metric-span"), "value": metric, "disabled": False} for metric in all_metrics]
            return None, {"run_datetime": upload_store["run_datetime"]}, "primary", "Run", [False]*5, [False]*len(upload_store["parameters"]), metrics_list, 'multi'
        raise PreventUpdate
    
    data = data or {'clicks': 0}
    data['clicks'] = data['clicks'] + 1

    metrics_list = [{"label": html.Span(metric, className = "metric-span"), "value": metric, "disabled": False} for metric in all_metrics]
    
    if n_clicks % 2 == 1:

        # date time for run folder
        cur_datetime = f"{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}"
        datetime_store = {"run_datetime": cur_datetime}
        
        # copy dakota.in to run folder
        os.makedirs(f"./runs/{cur_datetime}/")
        shutil.copy(f"./dakota/{config_store['config_name']}/{machine_store['machine']}/dakota.in", f"./runs/{cur_datetime}/")
        os.makedirs(f"./runs/{cur_datetime}/plots/")

        # make run config file
        run_config = [config_store, experiments_store, datetime_store, optimizer_store, metrics_store, parameters_store, machine_store]
        with open(f"./runs/{cur_datetime}/run_config.yaml", 'w') as config_file:
            yaml.dump(run_config, config_file)
        
        # start optimization subprocess
        logging.info("Lanching Dakota")
        out_file = open(f"./runs/{cur_datetime}/dakota.out", "a")
        print(f"dakota/{config_store['config_name']}/{machine_store['machine']}/run_local_job.sh {cur_datetime}")
        dakota_process = subprocess.Popen(f"dakota/{config_store['config_name']}/{machine_store['machine']}/run_local_job.sh {cur_datetime}", shell=True, stdout=out_file, stderr=out_file)
        logging.info(f"Dakota running with PID: {dakota_process.pid}")
        
        metrics_list = [{"label": html.Span(metric, className = "metric-span"), "value": metric, "disabled": True} for metric in all_metrics]
        return data, datetime_store, "danger", "Stop", [True]*5, [True]*len(parameters_store["parameters"]), metrics_list, False
    
    if n_clicks != 0:
        logging.info("Attempting to shut down Dakota")
        process = subprocess.Popen(['pkill', '-9', '-f', 'dakota'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        logging.info(f"Kill log: {out}")
        metrics_list = [{"label": html.Span(metric, className = "metric-span"), "value": metric, "disabled": False} for metric in all_metrics]
        return '', run_datetime, "primary", "Run", [False]*5, [False]*len(parameters_store["parameters"]), metrics_list, 'multi'

    return data, {"run_datetime": ""}, "primary", "Run", [False]*5, [False]*len(parameters_store["parameters"]), metrics_list, 'multi'

@callback([Output('dakota-status', 'children'),
           Output('pareto-store', 'data'),
           Output('interval-component', 'interval')
          ],[
          Input('button_memory', 'data'),
          Input('metrics-store', 'data'),
          Input('interval-component', 'n_intervals'),
          Input('upload-store', 'data')],
          State('run-datetime-store', 'data'))
def on_data(ts, store, n, upload_store, run_datetime):

    metrics = store['metrics']
    metrics = [i.replace(" ","_") for i in metrics]

    iteration = 0
    metrics_dict = {}
    dakota_status = []
    dakota_status_text = ""
    plots = []
    
    if upload_store and ts is None:
        with open(f"./runs/{upload_store['run_datetime']}/dakota.out") as file:
            lines = [line.rstrip() for line in file]
            split_index = [idx for idx, s in enumerate(lines) if 'End DAKOTA input file' in s]

            if len(split_index) == 0:
                return [], -1, SHORT_INTERVAL_TIME
            else:
                split_index = split_index[0]

            input_list = lines[:split_index]
            output_list = lines[split_index:]

            for metric in metrics:

                metrics_dict[metric] = [i for i in output_list if metric in i]
                metrics_dict[metric] = [float(i.lstrip().split(" ")[0]) for i in metrics_dict[metric]]
        return [], metrics_dict, SHORT_INTERVAL_TIME

    if ts is None:
        return [html.Div(id='plots')], metrics_dict, SHORT_INTERVAL_TIME

    process = subprocess.Popen(['pgrep', '-f', 'run_local_job'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if(len(out) == 0):
        dakota_status_text = "Stopped"
        plots, iteration = get_dynamic_plots(metrics_dict, metrics, run_datetime["run_datetime"])
        dakota_status.append(html.H3(dakota_status_text, className = "column-header"))
        dakota_status.append(html.Div(id='plots'))
        dakota_status_container = html.Div(className = "optimization-column", children = dakota_status)
        return dakota_status_container, metrics_dict, LONG_INTERVAL_TIME
    else:
        plots, iteration = get_dynamic_plots(metrics_dict, metrics, run_datetime["run_datetime"])
        if iteration == -1:
            dots = get_dots(n)
            dakota_status_text = f"Initializing{dots}"
        else:
            dots = get_dots(n)
            dakota_status_text = f"Running Iteration {iteration + 1}{dots}"
    
    dakota_status.append(html.H3(dakota_status_text, className = "column-header"))
    dakota_status.append(html.Div(id='plots', children = plots))
    dakota_status_container = html.Div(className = "optimization-column", children = dakota_status)

    return dakota_status_container, metrics_dict, SHORT_INTERVAL_TIME

def get_dynamic_plots(metrics_dict, metrics, run_datetime):

    dynamic_plots = []

    with open(f"./runs/{run_datetime}/dakota.out") as file:
        lines = [line.rstrip() for line in file]

        split_index = [idx for idx, s in enumerate(lines) if 'End DAKOTA input file' in s]

        if len(split_index) == 0:
            return [], -1
        else:
            split_index = split_index[0]

        input_list = lines[:split_index]
        output_list = lines[split_index:]

        for metric in metrics:
            metrics_dict[metric] = [i for i in output_list if metric in i]
            metrics_dict[metric] = [float(i.lstrip().split(" ")[0]) for i in metrics_dict[metric]]
        
        for x in range(0, len(metrics)):
            y = metrics_dict[metrics[x]]
            if len(y) == 0:
                return [], 0
            fig = px.scatter(x=np.arange(1, len(y) + 1), y=y, title="Automatic")
            fig.update_layout(xaxis_title="Iteration", title={'text': metrics[x],'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top'})
            fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
            fig.update_yaxes(showline=True, linecolor='lightgray', showgrid=True, gridcolor='lightgray')
            fig.update_xaxes(showline=True, linecolor='lightgray', showgrid=True, gridcolor='lightgray')
            fig.write_image(f"./runs/{run_datetime}/plots/metric_{x}.png")
            dynamic_plots.append(dcc.Graph(id='metrics-graph'+str(x),figure=fig))
    
    return dynamic_plots, len(metrics_dict[metrics[0]])

def get_dots(n):
    return '.'*(n % 4)

@callback(Output('optimizer-sliders', 'children'), 
          Input('upload-store', 'data'),
          State('genetic-algorithm-config-store', 'data'),
          )
def update_optim_sliders(upload_store, ga_store):
    update_dict = upload_store.get("update_dict", {}) # TODO: Does this need to be a single-key dictionary of a dictionary?
    max_iterations_config = ga_store["max_iterations"]
    max_function_evaluations_config = ga_store["max_function_evaluations"]
    population_size_config = ga_store["population_size"]
    mutation_rate_config = ga_store["mutation_rate"]
    crossover_rate_config = ga_store["crossover_rate"]

    # TODO: This callback should reference the id's of the sliders rather than rewrite the html
    sliders = [
        html.Div(children = [
            dbc.Col(width=11, children=[
                html.H3("Genetic Algorithm Configuration"),
            ]),
            dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Genetic Algorithm Configuration"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                ]),
            ]),
            ], style = {"padding": "25px 15px 0 15px", "display": "flex"}),
        html.H5(max_iterations_config["name"], className="slider-header"),
        html.P(max_iterations_config["description"], className="slider-text"),
        dcc.Slider(max_iterations_config["min"], max_iterations_config["max"], max_iterations_config["step"],
                   value=update_dict.get("max_iterations", max_iterations_config["default"]),
                   marks={max_iterations_config["min"]:str(max_iterations_config["min"]), max_iterations_config["max"]:str(max_iterations_config["max"])},
                   tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 1}),
        html.H5(max_function_evaluations_config["name"], className="slider-header"),
        html.P(max_function_evaluations_config["description"], className="slider-text"),
        dcc.Slider(max_function_evaluations_config["min"], max_function_evaluations_config["max"], max_function_evaluations_config["step"],
                   value=update_dict.get("max_function_evaluations", max_function_evaluations_config["default"]),
                   marks={max_function_evaluations_config["min"]:str(max_function_evaluations_config["min"]), max_function_evaluations_config["max"]:str(max_function_evaluations_config["max"])},
                   tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 2}),
        html.H5(population_size_config["name"], className="slider-header"),
        html.P(population_size_config["description"], className="slider-text"),
        dcc.Slider(population_size_config["min"], population_size_config["max"], population_size_config["step"],
                   value=update_dict.get("population_size", population_size_config["default"]),
                   marks={population_size_config["min"]:str(population_size_config["min"]), population_size_config["max"]:str(population_size_config["max"])},
                   tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 3}),
        html.H5(mutation_rate_config["name"], className="slider-header"),
        html.P(mutation_rate_config["description"], className="slider-text"),
        dcc.Slider(mutation_rate_config["min"], mutation_rate_config["max"], mutation_rate_config["step"],
                   value=update_dict.get("mutation_rate", mutation_rate_config["default"]),
                   marks={mutation_rate_config["min"]:str(mutation_rate_config["min"]),mutation_rate_config["max"]:str(mutation_rate_config["max"])},
                   tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 4}),
        html.H5(crossover_rate_config["name"], className="slider-header"),
        html.P(crossover_rate_config["description"], className="slider-text"),
        dcc.Slider(crossover_rate_config["min"], crossover_rate_config["max"], crossover_rate_config["step"],
                   value=update_dict.get("crossover_rate", crossover_rate_config["default"]),
                   marks={crossover_rate_config["min"]:str(crossover_rate_config["min"]), crossover_rate_config["max"]:str(crossover_rate_config["max"])},
                   tooltip={"placement": "bottom", "always_visible": True}, id={"type": "optimizer-slider", "index": 5}),
        dbc.Button("Run", outline=False, color="primary", size='sm', id='button', style={"width": "100%", "font-size": "1.5rem", "margin-top": "30px"})
    ]
    
    return sliders




