import dash
import string
import jinja2
import pdfkit
import shutil
import os
import logging
import subprocess

from dash                        import dcc, MATCH
from dash                        import html
from dash                        import dash_table
from dash                        import callback, Input, Output, State
from sklearn.cluster             import KMeans
from kneed                       import KneeLocator
from sklearn.decomposition       import PCA
from dash.exceptions             import PreventUpdate
from sklearn.metrics             import pairwise_distances_argmin_min
from dash                        import ALL

import plotly.express            as px
import numpy                     as np
import pandas                    as pd
import dash_bootstrap_components as dbc
import plotly.io                 as pio



def get_param_history(dakota_data_file):

    data = open(dakota_data_file, "rb").read().splitlines()

    df = pd.DataFrame(columns=[t.decode('ASCII') for t in data[0].split()])

    params = list(df.keys())

    params_dict = {}
    for param in params:
        params_dict[param] = []

    for l in range(1,len(data)):
        for param in params_dict.keys():
            data_l = data[l].split()
            params_dict[param].append(data_l[params.index(str(param))])

    del params_dict['interface']
    del params_dict['%eval_id']

    max_metric_keys = [i for i in params_dict.keys() if "maximize" in i.lower()]
    for key in max_metric_keys:
        del params_dict[key]

    min_metric_keys = [i for i in params_dict.keys() if "minimize" in i.lower()]
    for key in min_metric_keys:
        del params_dict[key]

    params_np = params_dict.values()
    params_np = list(params_np)
    params_np = np.array(params_np).T
    params_np = params_np.astype(float)

    params = list(params_dict.keys())

    return params, params_np

layout = html.Div([
    html.Div(className="content-header", children=[
        dbc.Row(children=[
            dbc.Col(width=11, children=[
                html.H1("Optimization Summary")
                ], style={"padding-left": "8.3%", "text-align": "center"}),
            dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Optimization Summary"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                    ]),
                ]),
        ]),
    ], style={"margin-top": "25px"}),
    dbc.Row([
        dbc.Row(children=[
            dbc.Col(width=1),
            dbc.Col(width=4, children=[
                html.H1("Configuration Search Space", style={"padding-left": "24px"})
            ]),
            dbc.Col(width=1, style={"align-content": "center", "text-align": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Configuration Search Space"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={"width": "24px"}),
                ]),
            ]),
            dbc.Col(width=5, children=[
                html.H1("Configuration Database")
            ], style={"padding-left": "72px"}),
            dbc.Col(width=1, style={"align-content": "center", "text-align": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Configuration Database"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                ]),
            ]),
        ]),
        dbc.Row(children=[
            dbc.Col([
                        dcc.Dropdown(id='y_axis_dropdown'),
                ], width=1),
            dbc.Col([
                        dcc.Graph(id='scatterplot'),
                        dcc.Dropdown(id='x_axis_dropdown', style={"margin":"36px auto"}),
                ], width=5, style={"padding": "36px"}),
            dbc.Col([
                html.Br(),
                html.Div(id = "config-container", children=[
                    dash_table.DataTable(
                        id="pareto-table",
                        columns=[],
                        data=[],
                        row_selectable="multi",
                        row_deletable=False,
                        editable=False,
                        selected_rows = [],
                        filter_action="native",
                        sort_action="native",
                        style_table={"overflowX": "auto", 'height':500},
                        style_cell={
                                    'textOverflow': 'ellipsis',
                                    'textAlign': 'center',
                                    'height': 'auto',
                                    'whiteSpace': 'normal',
                                    'minWidth': 250,
                                    'width': 250,
                                    'maxWidth': 250,
                        }
                    )
                ], style={"padding-left": "72px"}),
            ], width=6, style={"padding-left": "0px"}),
        ])
    ], className="summary-header"),

    html.Br(),

    html.Div(className="content-header", children=[
        dbc.Row(children=[
            dbc.Col(width=11, children=[
                html.H1("Optimization Histograms")
                ], style={"padding-left": "8.3%", "text-align": "center"}),
            dbc.Col(width=1, style={"align-content": "center", "padding": "0"}, children=[
                html.Button(id={"type":'modal-button', "name":"Optimization Histograms"}, className="modal-button", children=[
                    html.Img(src="/assets/ModalQuestionMark.svg", style={'width': '24px'}),
                    ]),
                ]),
        ]),
    ], style={"margin-bottom": "0px"}),
    dbc.Row([
        dbc.Col([
            html.Div(id="histogramBlock", style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-around'}),
        ]),
    ], className="summary-histograms"),

    html.Br(),


], className = "")


@callback(
    Output('plot-store', 'data'),
    Input({"type": "metric-slider", "index": ALL}, "value"),
    Input('pareto-store', 'data'),
    State('plot-store', 'data'),

)
def initial_callback(values, pareto_store, plot_store):

    if pareto_store == {}:
        raise PreventUpdate

    metrics = list(pareto_store.keys())
    metrics = [i.split("_")[1]+" ("+i.split("_")[0]+")" for i in metrics]

    ps_np = pareto_store.values()
    ps_np = list(ps_np)
    ps_np = np.array(ps_np).T

    if ps_np.shape[0] == 0:
        return plot_store      

    param_names, param_data = get_param_history("dakota_data.dat")

    if ps_np.shape[0] != param_data.shape[0]:
        # Load plot_stores' param data; this will happen on a load config event
        param_data = plot_store["params_data"]
        param_names = plot_store["params_names"]
    else:
        plot_store = {}
        if ps_np.shape[0] == 0:
            return plot_store

    plot_store["metrics_data"] = ps_np
    plot_store["metrics_names"] = metrics

    plot_store["params_data"] = param_data 
    plot_store["params_names"] = param_names

    plot_store['slider_mins'] = []
    plot_store['slider_maxs'] = []

    if len(values) != 0:
        plot_store['sliders'] = values       
    else:
        plot_store['sliders'] = []

    for x in range(0, ps_np.shape[1]):
        plot_store['slider_mins'].append(np.nanmin(ps_np[:,x]))
        plot_store['slider_maxs'].append(np.nanmax(ps_np[:,x]))
        if len(values) == 0:
            plot_store['sliders'].append([np.nanmin(ps_np[:,x]),np.nanmax(ps_np[:,x])])

    return plot_store

@callback(
    Output('scatterplot', 'figure'),
    Output('pareto-table', 'columns'),
    Output('pareto-table', 'data'),
    Output('x_axis_dropdown', 'options'),
    Output('x_axis_dropdown', 'value'),
    Output('y_axis_dropdown', 'options'),
    Output('y_axis_dropdown', 'value'),
    Output('histogramBlock', 'children'),
    Output('config-search-space-raw', 'data'),
    Output('config-search-space-filtered', 'data'),
    Input('plot-store', 'data'),
    Input('x_axis_dropdown', 'value'),
    Input('y_axis_dropdown', 'value'),
    Input('run-datetime-store', 'data'),
)
def update_graph(plot_store, x_axis, y_axis, run_datetime):

    process = subprocess.Popen(['pgrep', '-f', 'run_local_job'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if plot_store == {} or len(out) != 0:
        raise PreventUpdate

    if x_axis is None:
        # If more than 2 metrics are being optimized, add a PCA view
        if len(plot_store['metrics_names']) >= 3:
            x_axis = 'PCA 0'
            x_axis_default = 'PCA 0'
        else:
            x_axis_default = plot_store['metrics_names'][0]
            x_axis = plot_store['metrics_names'][0]
    else:
        x_axis_default = x_axis

    if y_axis is None:
        # If more than 2 metrics are being optimized, add a PCA view
        if len(plot_store['metrics_names']) >= 3:
            y_axis = 'PCA 1'
            y_axis_default = 'PCA 1'
        else:
            y_axis_default = plot_store['metrics_names'][1]
            y_axis = plot_store['metrics_names'][1]
    else:
        y_axis_default = y_axis

    ps_metrics = np.stack(plot_store['metrics_data'])
    ps_params = np.stack(plot_store['params_data'])

    if ps_metrics.shape[0] != ps_params.shape[0]:
        raise PreventUpdate  

    # If more than 2 metrics are being optimized, add a PCA view
    if len(plot_store['metrics_names']) >= 3:

        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(ps_metrics)

        ps_np = np.concatenate((ps_metrics,ps_params, pca_features), axis=1)
        ps_names = plot_store['metrics_names'] + plot_store['params_names']
        ps_names.append("PCA 0")
        ps_names.append("PCA 1")

    else:

        ps_np = np.concatenate((ps_metrics,ps_params), axis=1)
        ps_names = plot_store['metrics_names'] + plot_store['params_names']

    # ps_np1 is the nonfiltered results, but only includes the metrics in addition to a bool indicating if filtered
    ps_np1 = np.zeros((ps_metrics.shape[0], ps_metrics.shape[1]+1))
    ps_np1[:,:ps_metrics.shape[1]] = ps_metrics

    # ps_raw is the raw pareto front results with all parameters & metrics, including PCA
    ps_raw = ps_np

    for x in range(0,ps_metrics.shape[1]):
        ps_np1[ps_np1[:, x] < plot_store['sliders'][x][0], ps_metrics.shape[1]] = True
        ps_np1[ps_np1[:, x] > plot_store['sliders'][x][1], ps_metrics.shape[1]] = True
        ps_np = ps_np[ps_np[:,x] >= plot_store['sliders'][x][0]]
        ps_np = ps_np[ps_np[:,x] <= plot_store['sliders'][x][1]]

    # ps_np is the filtered pareto front results with the filtered parameters and metrics, including PCA
    df = pd.DataFrame(data    = ps_np,  
                      columns = ps_names)

    df2 = pd.DataFrame(data    = ps_np1,  
                       columns = plot_store['metrics_names'] + ["Filtered"])


    df2['Filtered'] = df2['Filtered'].astype('bool')

    scatter = px.scatter(df, x=x_axis, y=y_axis)
    #scatter.update_layout(title={'text' : "Configuration Search Space", 'x':0.5, 'xanchor': 'center'})
    #scatter.update_xaxes(range=[plot_store['slider_mins'][0], plot_store['slider_maxs'][0]])
    #scatter.update_yaxes(range=[plot_store['slider_mins'][0], plot_store['slider_maxs'][0]])
    scatter.update_traces(marker=dict(color='black'))

    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict("records")

    x_axis_options = plot_store['params_names'] + plot_store['metrics_names']
    y_axis_options = plot_store['params_names'] + plot_store['metrics_names']

    # If more than 2 metrics are being optimized, add a PCA view
    if len(plot_store['metrics_names']) >= 3:
        x_axis_options.append("PCA 0")
        y_axis_options.append("PCA 1")

    histogramBlock = []
    for x in range(0,len(plot_store['metrics_names'])):

        figure = px.histogram(df2, x=plot_store['metrics_names'][x], color='Filtered', color_discrete_map={True: "red", False: "black"})
        title = plot_store['metrics_names'][x]
        figure.update_layout(title={'text' : f'{title} Distribution', 'x':0.5, 'xanchor': 'center'})
        graph = dcc.Graph(figure=figure, config={'displayModeBar': False, 'staticPlot': True})

        graph_save_location = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "runs/" + run_datetime["run_datetime"] + "/plots/"
        if figure['data'][0]['x'].any():
           pio.write_image(figure, graph_save_location + "histogram_" + str(x) + '.png')

        min_val = plot_store['slider_mins'][x] - (plot_store['slider_mins'][x] * 0.01)
        max_val = plot_store['slider_maxs'][x] + (plot_store['slider_maxs'][x] * 0.01)
        slider = dcc.RangeSlider(min_val, max_val, value=plot_store['sliders'][x], marks={min_val:f'{min_val:.2f}',max_val:f'{max_val:.2f}'}, id={"type":'metric-slider', "index":x})
        histogramBlock.append(
            html.Div(
                children=[graph, html.Div(slider, style={'padding-left': '55px', 'padding-right': '55px', 'padding-top': '25px'})],
                style={'display': 'inline-block', 'width': '45%', 'padding': '10px'}
            )
        )

    return scatter, columns, data, x_axis_options, x_axis_default, y_axis_options, y_axis_default, histogramBlock, ps_raw, ps_np

@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Output('pareto-table', 'selected_rows', allow_duplicate=True),
    Output('filtered-table-store', 'data'),
    Input('scatterplot', 'selectedData'),
    Input('pareto-table', 'selected_rows'),
    Input('pareto-table', 'data'),
    State('cart-store', 'data'),
    State('plot-store', 'data'),
    State('filtered-table-store', 'data'),
    prevent_initial_call=True,
)
def update_graph(selected_data, filtered_selection, filtered_table_data, cart_store, full_table_data, filtered_table_store ):
    if (cart_store == {}):
        cart_store['configs'] = []
        cart_store['metrics'] = []
        return cart_store, [], []

    # Ensure the metrics for the selected configurations are stored in the cart store; used as ground truth in case the order changes
    cart_store['metrics'] = [ full_table_data['metrics_data'][idx] for idx in cart_store['configs']]

    # Create a reference list of the metrics currently shown in the table
    filtered_table_metrics = [[filtered_table_data[idx][name] for name in full_table_data['metrics_names']] for idx, value in enumerate(filtered_table_data)]

    # If the order of the list changed, or if the list was filtered, only select the configurations that remain and ensure
    # that you have the correct index of the selected configurations on the filtered list
    if filtered_table_data != filtered_table_store:
        selected_filtered_indices_full_table = []
        selected_filtered_metrics_full_table = []
        selected_filtered_indices_filtered_table = []
        for idx, metric_set in enumerate(cart_store['metrics']):
            index = next((i for i, values in enumerate(filtered_table_metrics) if values == metric_set), None)
            if index is not None:
                selected_filtered_indices_full_table.append(cart_store['configs'][idx])
                selected_filtered_metrics_full_table.append(metric_set)
                selected_filtered_indices_filtered_table.append(index)
        cart_store['configs'] = selected_filtered_indices_full_table
        cart_store['metrics'] = selected_filtered_metrics_full_table
        filtered_selection = selected_filtered_indices_filtered_table
        return cart_store, filtered_selection, filtered_table_data

    # If an item was unchecked, remove it
    if len(cart_store['configs']) > len(filtered_selection):
        selected_filtered_metrics = [ filtered_table_metrics[idx] for idx in filtered_selection]
        selected_indices_full_table = []
        selected_metrics_full_table = []
        for idx, metric in enumerate(cart_store['metrics']):
            if metric in selected_filtered_metrics:
                selected_indices_full_table.append(cart_store['configs'][idx])
                selected_metrics_full_table.append(metric)
        cart_store['metrics'] = selected_metrics_full_table
        cart_store['configs'] = selected_indices_full_table

    # Check if any new selections exist from the configuration search space. Add these to the full table list
    if selected_data is not None:
        for point in selected_data['points']:
            full_table_index = next((i for i, values in enumerate(full_table_data['metrics_data']) if values == filtered_table_metrics[point['pointIndex']]), None)
            if full_table_index not in cart_store['configs']:
                cart_store['configs'].append(full_table_index)
                cart_store['metrics'].append(full_table_data['metrics_data'][full_table_index])

    # Add new items that were checked
    if filtered_selection is not None:
        for filtered_index in filtered_selection:
            if filtered_table_metrics[filtered_index] not in cart_store['metrics']:
                full_table_index = next((i for i, values in enumerate(full_table_data['metrics_data']) if values == filtered_table_metrics[filtered_index]), None)
                cart_store['configs'].append(full_table_index)
                cart_store['metrics'].append(full_table_data['metrics_data'][full_table_index])

    ### Check the checkbox on all of the configurations that have been selected
    filtered_index_list = []
    for metric in cart_store['metrics']:
        index = next((i for i, values in enumerate(filtered_table_metrics) if values == metric), None)
        if index is not None:
            filtered_index_list.append(index)

    return cart_store, filtered_index_list, filtered_table_data

@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Output('cart-store-loader', 'data', allow_duplicate=True),
    Input('cart-store-loader', 'data'),
    prevent_initial_call=True,
)
def load_cart_store(cart_store_loader):
    if not cart_store_loader['loaded']:
        cart_store_loader['loaded'] = True
        return cart_store_loader, cart_store_loader
