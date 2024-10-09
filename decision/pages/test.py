from dash import html, callback, Input, Output, State, dcc, dash_table, no_update, ALL, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import os
import pdfkit
import jinja2
import logging
import shutil
import json
import yaml
import plotly.io                 as pio
import plotly.express            as px


import base64
import time
import subprocess

import pandas as pd

def make_aegis_config(config_dict):

    with open('OSIA/aegis_rockster_server/aegis_inference_config.yml', 'w') as file:
        file.write(f'mission: "m20"\n')
        file.write(f'instrument: "ncam"\n')
        file.write(f"smooth_window: {config_dict['smooth_window']}\n")
        file.write(f"sky_sigma_threshold: {config_dict['sky_sigma_threshold']}\n")
        file.write(f"hi_threshold: {config_dict['hi_threshold']}\n")
        file.write(f"lo_threshold: {config_dict['lo_threshold']}\n")
        file.write(f"gap_threshold: {config_dict['gap_threshold']}\n")

layout = html.Div([
    html.Div(id="test-page-implemented", children=[
        html.Div(children=[
            dbc.Row(children=[
                dbc.Col(width=6, children=[
                    html.H3("Select Images", style={"marginLeft": "15px"}),
                    dcc.Upload(
                        id='upload-experiments',
                        children=html.Div([
                            html.H5('Drag and Drop Here or '),
                            html.A('Click to Select .pgm Files'),
                            html.Br(),
                        ]),
                        style={
                            'width': '80%', 'height': '90px', 'lineHeight': '80px',
                            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                            'textAlign': 'center', 'margin': '10px'
                        },
                        # Allow multiple files to be uploaded, accept only .pgm files
                        multiple=True,
                        accept='.pgm, .png, .jpg, .jpeg'
                    ),
                ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                dbc.Col(width=3, children=[
                    dbc.Button("Download PDF", outline=False, color="primary", size='sm', id='download-pdf-button', style={"width": "100%", "font-size": "1.5rem", "margin-top": "30px"}),
                    dcc.Download(id="download-pdf"),
                ]),
                dbc.Col(width=3, children=[
                    dbc.Button("Save Session", outline=False, color="primary", size='sm', id='save-session-button', style={"width": "100%", "font-size": "1.5rem", "margin-top": "30px"}),
                    dcc.Download(id="download-config"),
                ]),
            ]),
        ]),

        html.Div(children=[
            dbc.Row(children=[
                dbc.Col(width=5, children=[
                    dcc.RadioItems(id='uploaded-image-radio-buttons', options=[], style={"marginLeft": "15px"}),
                    html.Div(id="configuration-data", style={"marginTop": "15px", "marginLeft": "15px"}, children=[
                        dash_table.DataTable(
                            id="config-table",
                            columns=[],
                            data=[],
                            row_selectable="single",
                            row_deletable=False,
                            cell_selectable=False,
                            editable=False,
                            selected_rows = [],
                            sort_action="native",
                            style_table={"overflowX": "auto", 'height':500},
                            style_cell={
                                        'textOverflow': 'ellipsis',
                                        'textAlign': 'center',
                                        'height': 'auto',
                                        'whiteSpace': 'normal',
                                        'minWidth': 50,
                                        'width': 100,
                                        'maxWidth': 150,
                            }
                        )
                    ])
                ]),
                dbc.Col(width=7, children=[
                    html.Img(id='test-image', src='', style={"display": "none"})
                ]),
            ]),
        ]),
    ]),
    html.Div(id="test-page-not-implemented", style={"display": "none"}, children=[
        html.H2("Test Page not implemented for this project.", style={"textAlign": "center"})
    ]),
])

@callback(
    Output('uploaded-image-radio-buttons', 'options'),
    Output('test-image-store', 'data'),
    Output('upload-experiments', 'contents'),
    Input('upload-experiments', 'contents'),
    Input('test-image-store', 'data'),
)
def upload_test_image(contents, image_store):
    if contents != None:
        image_store.append(contents[0])
    image_options = []
    for idx, item in enumerate(image_store):
        image_options.append({
            "label": [html.Img(src=item, style={"width":"150px", "marginLeft": "25px", "marginTop": "10px"}),
                      dbc.Button('Delete', id={"type": "image-delete-button", "index": idx}, style={"marginLeft": "25px"})],
            "value": idx,
        })
    return image_options, image_store, None

@callback(
    Output('global-alerts', 'children', allow_duplicate=True),
    Output('test-status', 'data'),
    Input('test-status', 'data'),
    Input('uploaded-image-radio-buttons', 'value'),
    Input('config-table', 'selected_rows'),
    prevent_initial_call=True,
)
def test_status(status, image_idx, selected_config):
    if image_idx != None:
        if selected_config != None and selected_config != []:
            if status == "standby":
                return dbc.Alert("Running Analysis", color="info", duration=30000, dismissable=True), "running"
            if status == "running":
                return dbc.Alert("Running Analysis", color="info", duration=30000, dismissable=True), "running"
            elif status == "done":
                return dbc.Alert("Analysis Complete", color="success", duration=4000, dismissable=True), "standby"
    raise PreventUpdate

@callback(
    Output('config-table', 'selected_rows'),
    Input('cart-store', 'data'),
    State('config-table', 'selected_rows'),
    State('config-table', 'data'),
    prevent_initial_call=True,
)
def reset_selection(cart_store, selected_rows, config_table_data):
    if cart_store is None:
        raise PreventUpdate
    # If any of the values in the config table are different from what's in the cart store unselect the configuration
    elif {tuple(table_data.values()) for table_data in config_table_data} != {tuple(metric) for metric in cart_store['metrics']}:
        return []
    else:
        raise PreventUpdate

@callback(
    Output('test-image', 'src'),
    Output('test-image', 'style'),
    Output('test-status', 'data', allow_duplicate=True),
    Input('uploaded-image-radio-buttons', 'value'),
    Input('config-table', 'selected_rows'),
    State('test-image-store', 'data'),
    State('plot-store', 'data'),
    State('cart-store', 'data'),
    State('run-datetime-store', 'data'),
    prevent_initial_call=True,
)
def display_test_image(image_idx, selected_config, image_store, configuration_data, configuration_options, run_datetime):
    if image_idx == None:
        raise PreventUpdate
    elif selected_config == None or selected_config == []:
        return image_store[image_idx], {"display": "block", "maxHeight": "750px", "alignContent": "left"}, "standby"
    else:
        # Gather the selected config data
        configuration_names = configuration_data['params_names']
        selected_config_parameters = configuration_data['params_data'][configuration_options['configs'][selected_config[0]]]
        selected_config_dict = dict(zip(configuration_names, selected_config_parameters))

        image_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/output_image.png"
        if os.path.exists(image_save_location):
            os.remove(image_save_location)

        make_aegis_config(selected_config_dict)

        img_bytes = base64.b64decode(image_store[image_idx].split(",")[1])

        if not os.path.exists('aegis_inference/'):
            os.makedirs('aegis_inference/')

        with open('aegis_inference/input_image.png', 'wb') as file:
            file.write(img_bytes)

        # Call AEGIS inference API
        aegis_inference_job = subprocess.run(f"dakota/AEGIS/local/aegis_inference.sh", shell=True)

        output_image = 'aegis_inference/output_image.png'
        while not os.path.exists(output_image):
            time.sleep(1)  # Wait for 1 second before checking again

        shutil.copy(output_image, image_save_location)

        with open(output_image, 'rb') as img_file:
            img_bytes = img_file.read()

        encoding =  base64.b64encode(img_bytes).decode('utf-8')
        img_bytes = "data:image/png;base64," + encoding

        os.remove(output_image)

        return img_bytes, {"display": "block", "maxHeight": "750px", "alignContent": "left"}, "done"


@callback(
    Output('config-table', 'columns'),
    Output('config-table', 'data'),
    Input('cart-store', 'data'),
    State('plot-store', 'data'),
    prevent_initial_call=True,
)
def populate_configuration_table(selected_configuration, configuration_data):
    if selected_configuration.get('configs', []) == [] or configuration_data == {}:
        return [], []
    else:
        data = []
        for row in selected_configuration['configs']:
            current_set = {}
            for idx, column in enumerate(configuration_data['metrics_names']):
                current_set[column] = configuration_data['metrics_data'][row][idx]
            data.append(current_set)
        columns = [{"name": i, "id": i} for i in configuration_data['metrics_names']]
        return columns, data

@callback(
    Output('global-alerts', 'children', allow_duplicate=True),
    Output('download-pdf', 'data'),
    Input('download-pdf-button', 'n_clicks'),
    State('config-table', 'selected_rows'),
    State('plot-store', 'data'),
    State('cart-store', 'data'),
    State('uploaded-image-radio-buttons', 'value'),
    State('experiments-store', 'data'),
    State('config-store', 'data'),
    State('parameters-store', 'data'),
    State('optimizer-store', 'data'),
    State('genetic-algorithm-config-store', 'data'),
    State('run-datetime-store', 'data'),
    State('config-search-space-raw', 'data'),
    State('config-search-space-filtered', 'data'),
    prevent_initial_call=True,
)
def download_pdf(download_pdf, selected_config, configuration_data, configuration_options, image_idx,
                 experiments_store, config_store, parameters_store, optimizer_store, ga_config_store,
                 run_datetime, config_search_space_raw, config_search_space_filtered):
    '''Generate PDF report from cached products'''
    if image_idx == None:
        return dbc.Alert("Please select an image.", color="danger", duration=4000), no_update

    if selected_config == []:
        return dbc.Alert("Please select a configuration.", color="danger", duration=4000), no_update

    test_image_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/output_image.png"
    if not os.path.exists(test_image_location):
        return dbc.Alert("Please await for analysis to complete.", color="danger", duration=4000), no_update

    options = { "enable-local-file-access": None }

    with open(config_store['config_path']) as f:
        config = yaml.safe_load(f)
        metrics_descriptions = config['metrics']['description']
        optimization_parameter_config = config['parameters'][0]['parameters']

    optimization_parameter_config_name_to_variable = {item['name']: item['variable_name'] for item in optimization_parameter_config}

    # Creates table for "Data Sets" Section
    experiment_info = ""
    # TODO: Make this generalized for projects with verying experiment entries
    experiment_info = pd.DataFrame([{'Experiment Name': name, "Experiment ID": id} for name, id in zip(experiments_store['Name'], experiments_store['ID'])])
    experiment_info = experiment_info.to_html(index=False, border=1, classes="metrics_table")
    experiment_info = experiment_info

    # Creates table for "Optimization Metrics" Section
    metrics_names = []
    metrics_optimization_objective = []
    for item in configuration_data['metrics_names']:
        name = item.split('(')[0].strip()
        objective = item.split('(')[1].strip(')').strip()
        metrics_names.append(name)
        metrics_optimization_objective.append(objective)
    metrics_info = pd.DataFrame([{'Metric': metric, "Optimization Objective": objective, 'Description': description} for metric, objective, description in zip(metrics_names, metrics_optimization_objective, metrics_descriptions)])
    optimization_metrics = metrics_info.to_html(index=False, border=1, classes="metrics_table")

    # Creates table for "Optimization Parameters" Section
    optimization_parameter_names = []
    optimization_parameter_description = []
    optimization_parameter_range = [] # "min - max"
    optimization_parameter_selected_range = [] # tuples (low,high)
    for item in optimization_parameter_config:
        optimization_parameter_names.append(item['name'])
        optimization_parameter_description.append(item['description'])
        optimization_parameter_range.append(str(item['min_range']) + " - " + str(item['max_range']))
        temp_parameter_range = parameters_store['parameters'][parameters_store['names'].index(item['variable_name'])]
        optimization_parameter_selected_range.append(str(temp_parameter_range[0]) + " - " + str(temp_parameter_range[1]))
    optimization_parameters = pd.DataFrame([{'Parameter': name, "Description": description, "Available Range": available_range, "Selected Range": selected_range}
                                            for name, description, available_range, selected_range in zip(optimization_parameter_names, optimization_parameter_description, optimization_parameter_range, optimization_parameter_selected_range)])
    optimization_parameters = optimization_parameters.to_html(index=False, border=1, classes="metrics_table")

    # Creates table for "Genetic Algorithm Configuration" section
    optimizer_store = optimizer_store["update_dict"]
    ga_parameter_names = []
    ga_parameter_descriptions = []
    ga_parameter_range = []
    ga_parameter_selected_value = []
    for item in ga_config_store:
        ga_parameter_names.append(ga_config_store[item]["name"])
        ga_parameter_descriptions.append(ga_config_store[item]["description"])
        ga_parameter_range.append(str(ga_config_store[item]["min"]) + " - " + str(ga_config_store[item]["max"]))
        ga_parameter_selected_value.append(optimizer_store[item])
    GA_configuration = pd.DataFrame([{'Parameter': name, "Description": description, "Range of Values": available_values, "Selected Value": selected_value}
                                                for name, description, available_values, selected_value in zip(ga_parameter_names, ga_parameter_descriptions, ga_parameter_range, ga_parameter_selected_value)])
    GA_configuration = GA_configuration.to_html(index=False, border=1, classes="metrics_table")

    # Load GA performance metric plots
    GA_performance = ""
    plot_path = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/"
    for m in range(0, len(metrics_names)):
        GA_performance = GA_performance + f'<div style=\"display: inline-block; width: 45%; padding: 10px;\"><img src="{plot_path}metric_{m}.png"/></div>'

    # Creates table for Candidate Configurations
    # Use configuration_data for "Candidate Configurations"
    candidate_configurations = {}
    candidate_parameter_data = [configuration_data['params_data'][i] for i in configuration_options['configs']]
    candidate_parameter_results = {key: list(values) for key, values in zip(configuration_data['params_names'], zip(*candidate_parameter_data))}
    candidate_metrics_data = [configuration_data['metrics_data'][i] for i in configuration_options['configs']]
    candidate_configurations = {key: list(values) for key, values in zip(configuration_data['metrics_names'], zip(*candidate_metrics_data))}

    for key in optimization_parameter_config_name_to_variable:
        candidate_configurations[key] = candidate_parameter_results[optimization_parameter_config_name_to_variable[key]]
    candidate_configurations = pd.DataFrame(candidate_configurations)
    candidate_configurations = candidate_configurations.to_html(index=False, border=1, classes="metrics_table")

    # Creates table for Selected Configuration
    selected_configuration = {}
    parameter_names = configuration_data['params_names']
    selected_parameter_data = configuration_data['params_data'][configuration_options['configs'][selected_config[0]]]
    selected_parameter_dict = dict(zip(parameter_names, selected_parameter_data))
    selected_metrics_data = configuration_data['metrics_data'][configuration_options['configs'][selected_config[0]]]
    selected_configuration = dict(zip(configuration_data['metrics_names'], selected_metrics_data))

    for key in optimization_parameter_config_name_to_variable:
        selected_configuration[key] = selected_parameter_dict[optimization_parameter_config_name_to_variable[key]]
    selected_configuration = pd.DataFrame([selected_configuration])
    selected_configuration = selected_configuration.to_html(index=False, border=1, classes="metrics_table")

    test_image = f'<center><img src="{test_image_location}"/></center>'

    histograms = ''
    histogram_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/"
    for filename in os.listdir(histogram_location):
        file_path = os.path.join(histogram_location, filename)
        if os.path.isfile(file_path) and "histogram_" in filename:
            histograms += f'<div style=\"display: inline-block; width: 45%\"><img src="{file_path}"/></div>'

    ps_names = configuration_data['metrics_names'] + configuration_data['params_names']
    pareto_front_metrics_options = configuration_data['metrics_names']

    # If more than 2 metrics are being optimized, add a PCA view
    if len(configuration_data['metrics_names']) >= 3:
        ps_names.append("PCA 0")
        ps_names.append("PCA 1")
        pareto_front_metrics_options.append("PCA 0")
        pareto_front_metrics_options.append("PCA 1")

    filtered_configuration_search_space = pd.DataFrame(data = config_search_space_filtered, columns = ps_names)
    raw_configuration_search_space = pd.DataFrame(data = config_search_space_raw, columns = ps_names)

    raw_pareto_front_metrics = ''
    cur_idx = 0
    combinations = []
    for x_axis_option in pareto_front_metrics_options:
        for y_axis_option in pareto_front_metrics_options:
            if (x_axis_option != y_axis_option and (x_axis_option, y_axis_option) not in combinations and (y_axis_option, x_axis_option) not in combinations):
                combinations.append((x_axis_option, y_axis_option))
                pdf_scatter = px.scatter(raw_configuration_search_space, x=x_axis_option, y=y_axis_option)
                pdf_scatter.update_traces(marker=dict(color='black'))
                graph_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/raw_metrics_scatter_" + str(cur_idx) + ".png"
                pio.write_image(pdf_scatter, graph_save_location)
                raw_pareto_front_metrics += f'<div style=\"display: inline-block; width: 45%; padding: 10px;\"><img src="{graph_save_location}"/></div>'
                cur_idx += 1

    raw_pareto_front_metrics_to_params = ''
    cur_idx = 0
    combinations = []
    for x_axis_option in ps_names:
        for y_axis_option in ps_names:
            if (x_axis_option != y_axis_option and (x_axis_option, y_axis_option) not in combinations and (y_axis_option, x_axis_option) not in combinations
                and (x_axis_option in configuration_data['metrics_names'] or y_axis_option in configuration_data['metrics_names'])
                and (x_axis_option not in configuration_data['metrics_names'] or y_axis_option not in configuration_data['metrics_names'])):
                combinations.append((x_axis_option, y_axis_option))
                pdf_scatter = px.scatter(raw_configuration_search_space, x=x_axis_option, y=y_axis_option)
                pdf_scatter.update_traces(marker=dict(color='black'))
                graph_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/raw_params_scatter_" + str(cur_idx) + ".png"
                pio.write_image(pdf_scatter, graph_save_location)
                raw_pareto_front_metrics_to_params += f'<div style=\"display: inline-block; width: 45%; padding: 10px;\"><img src="{graph_save_location}"/></div>'
                cur_idx += 1

    filtered_pareto_front_metrics = ''
    cur_idx = 0
    combinations = []
    for x_axis_option in pareto_front_metrics_options:
        for y_axis_option in pareto_front_metrics_options:
            if (x_axis_option != y_axis_option and (x_axis_option, y_axis_option) not in combinations and (y_axis_option, x_axis_option) not in combinations):
                combinations.append((x_axis_option, y_axis_option))
                pdf_scatter = px.scatter(filtered_configuration_search_space, x=x_axis_option, y=y_axis_option)
                pdf_scatter.update_traces(marker=dict(color='black'))
                graph_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/filtered_metrics_scatter_" + str(cur_idx) + ".png"
                pio.write_image(pdf_scatter, graph_save_location)
                filtered_pareto_front_metrics += f'<div style=\"display: inline-block; width: 45%; padding: 10px;\"><img src="{graph_save_location}"/></div>'
                cur_idx += 1

    filtered_pareto_front_metrics_to_params = ''
    cur_idx = 0
    combinations = []
    for x_axis_option in ps_names:
        for y_axis_option in ps_names:
            if (x_axis_option != y_axis_option and (x_axis_option, y_axis_option) not in combinations and (y_axis_option, x_axis_option) not in combinations
                and (x_axis_option in configuration_data['metrics_names'] or y_axis_option in configuration_data['metrics_names'])
                and (x_axis_option not in configuration_data['metrics_names'] or y_axis_option not in configuration_data['metrics_names'])):
                combinations.append((x_axis_option, y_axis_option))
                pdf_scatter = px.scatter(filtered_configuration_search_space, x=x_axis_option, y=y_axis_option)
                pdf_scatter.update_traces(marker=dict(color='black'))
                graph_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/filtered_params_scatter_" + str(cur_idx) + ".png"
                pio.write_image(pdf_scatter, graph_save_location)
                filtered_pareto_front_metrics_to_params += f'<div style=\"display: inline-block; width: 45%; padding: 10px;\"><img src="{graph_save_location}"/></div>'
                cur_idx += 1

    # populate contents generated above
    context = {'parameters': optimization_parameters,
            'optimization_metrics': optimization_metrics,
            'experiment_names': experiment_info,
            'GA_configuration': GA_configuration,
            'GA_performance': GA_performance,
            'candidate_configurations': candidate_configurations,
            'selected_configuration': selected_configuration,
            'raw_pareto_front_metrics': raw_pareto_front_metrics,
            'raw_pareto_front_params': raw_pareto_front_metrics_to_params,
            'histograms': histograms,
            'filtered_pareto_front_metrics': filtered_pareto_front_metrics,
            'filtered_pareto_front_params': filtered_pareto_front_metrics_to_params,
            'test_image': test_image,
            }

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    # render report using context in report_template.html template
    html_template = 'report_template.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    # Generate PDF to be downloaded by download buttons upon press
    try:
        config = pdfkit.configuration()
        pdf = pdfkit.from_string(output_text, configuration=config, css='assets/style.css', options=options)
        return dbc.Alert("PDF download successful.", color="success", duration=10000, dismissable=True), dcc.send_bytes(pdf, filename="DECISION_Summary_Report.pdf")
    except OSError:
        logging.error("Please add the wkhtmltopdf executable to $PATH.")
        return dbc.Alert("Download failed. Please add the wkhtmltopdf executable to $PATH", color="danger", duration=4000), no_update

@callback(
    Output('global-alerts', 'children', allow_duplicate=True),
    Output('download-config', 'data'),
    Input("save-session-button", "n_clicks"),
    State("run-datetime-store", 'data'),
    State('test-image-store', 'data'),
    State('plot-store', 'data'),
    State('cart-store', 'data'),
    prevent_initial_call=True,
)
def download_selected_config(download_config_button, run_datetime_store, test_image_store, plot_store, cart_store):
    if run_datetime_store["run_datetime"] == "":
        raise PreventUpdate
    datetime = run_datetime_store["run_datetime"]
    zip_path = f"./runs/{datetime}"
    ui_settings = {
        "test-image-store": test_image_store,
        "plot-store": plot_store,
        "cart-store": cart_store
    }
    # File path
    file_path = os.path.join(zip_path, 'ui_status.json')

    # Writing JSON data to a file
    with open(file_path, 'w') as file:
        json.dump(ui_settings, file, indent=4)
    shutil.make_archive(zip_path, 'zip', zip_path)
    return dbc.Alert("Session download successful.", color="success", duration=4000), dcc.send_file(zip_path + ".zip")

@callback(
    Output("test-page-implemented", "style"),
    Output("test-page-not-implemented", "style"),
    Input("config-store", "data")
)
def page_implemented_notification(config):
    implemented_configs = ["AEGIS"]
    if config['config_name'] in implemented_configs:
        return {"display": "block"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "block"}


@callback(
    Output('test-image-store', 'data', allow_duplicate=True),
    Input({"type":"image-delete-button", "index": ALL }, "n_clicks"),
    State('test-image-store', 'data'),
    prevent_initial_call=True,
)
def upload_test_image(n_clicks, image_store):
    triggered_id = ctx.triggered_id
    button_index = triggered_id["index"] if triggered_id else None
    if button_index is not None and image_store:
        image_store.pop(button_index)
    return image_store