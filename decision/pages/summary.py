import dash
import string
import jinja2
import pdfkit
import shutil
import os
import logging

from dash                        import dcc, MATCH
from dash                        import html
from dash                        import dash_table
from dash                        import callback, Input, Output, State
from sklearn.cluster             import KMeans
from kneed                       import KneeLocator
from sklearn.decomposition       import PCA
from dash.exceptions             import PreventUpdate
from sklearn.metrics             import pairwise_distances_argmin_min
from dash_extensions             import Download
from dash_extensions.snippets    import send_file

import plotly.express            as px
import numpy                     as np
import pandas                    as pd
import dash_bootstrap_components as dbc
import dash_html_components      as html

def generate_pdf_report(summary_store, experiments_store, dropdown, report_name):
    '''Generate PDF report from cached products'''
    options = {
      "enable-local-file-access": None
    }
    plot_path = os.path.dirname(os.path.realpath(__file__)).rstrip("pages") + "plots/"

    # If plot folder does not exist, create it
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    param_data = np.asarray(summary_store["param_data"], dtype=np.float32)
    param_names = summary_store["param_names"]
    closest = summary_store["closest"]
    cluster_names = summary_store["cluster_names"]
    metrics_data = np.asarray(summary_store["metrics_data"], dtype=np.float32)
    metrics_names = summary_store["metrics_names"]

    parameters = ""
    metrics = ""
    experiment_names = ""
    ac_col_dropdown = []

    a_params = param_data[closest[string.ascii_lowercase.index(dropdown.lower())],:]
    a_metrics = metrics_data[closest[string.ascii_lowercase.index(dropdown.lower())],:]
    dictA = dict(zip(param_names, a_params))
    ac_col_dropdown.append(html.Br())
    for key, value in dictA.items():
        parameters = parameters + f"&emsp;{key}: {value:0.2f}<br>"
        ac_col_dropdown.append(html.H5(f"{key}: {value:0.2f}"))

    for m in range(0, len(metrics_names)):
        metrics = metrics + f"&emsp;{metrics_names[m]}: {a_metrics[m]:0.2f}<br>"

    # build string of html with metric plot source locations for PDF rendering 
    metric_plots = ""
    for m in range(0, len(metrics_names)):
        metric_plots = metric_plots + f'<center><img src="{plot_path}metric_{m}.png"/></center>'

    for experiment in experiments_store["experiment_names"]:
        experiment_names = experiment_names + f"&emsp;{experiment}<br>"

    # populate contents generated above
    context = {'parameters': parameters, 
               'metrics': metrics, 
               'plot_path': plot_path, 
               'metric_plots': metric_plots, 
               'experiment_names': experiment_names}

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    # render report using context in report_template.html template
    html_template = 'report_template.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    # Generate PDF to be downloaded by download buttons upon press
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    pdfkit.from_string(output_text, report_name, configuration=config, css='style.css', options=options)

    return ac_col_dropdown

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

def optimal_k(points, kmax):
    sse = []
    for k in range(1, kmax+1):
        kmeans = KMeans(n_clusters=k, n_init=10, max_iter=300,  tol=1e-04, random_state=0).fit(points)
        centroids = kmeans.cluster_centers_
        pred_clusters = kmeans.predict(points)
        curr_sse = 0
    
        for i in range(0,len(points)):
            curr_center = centroids[pred_clusters[i]]
            curr_sse += (points[i, 0] - curr_center[0]) ** 2 + (points[i, 1] - curr_center[1]) ** 2
      
        sse.append(curr_sse)

    # TODO - is there an off-by-one error here from starting k at 1?
    kn = KneeLocator(np.arange(0,len(sse)), sse, curve='convex', direction='decreasing')

    knee = kn.knee
    if knee is None:
        logging.info(f"Knee could not be found.  Setting to kmax ({kmax})")
        knee = kmax # TODO - in cases where knee cannot be found, setting to kmax.  Do we like this?

    if knee < 2:
        knee = 2 # TODO - We currently auto-populate the two columns with the first two clusters.
                 #          Cannot have less than two clusters, or things crash.  Can re-evaluate later.

    return knee

dash.register_page(__name__, title="Summary")

layout = html.Div([

    dbc.Row([
        dbc.Col(children=[

            html.Div(id='pareto-graph'),
            html.Div(id='cluster-table'),
            html.Br(),
            html.H3("System Notifications"),
            html.Br(),
                               
        ]),
        dbc.Col(children=[
            html.Br(),
            dcc.Dropdown(id='dropdown_col_1'),
            html.Div(id='analysis_col_1'),
            html.Br(),
            html.Button("Download Configuration", id="button-1"),
            Download(id="download-button-1")
        ]),
        dbc.Col(children=[
            html.Br(),
            dcc.Dropdown(id='dropdown_col_2'),
            html.Div(id='analysis_col_2'),
            html.Br(),
            html.Button("Download Configuration", id="button-2"),
            Download(id="download-button-2")
        ]),
    ]),
])

@callback([Output('pareto-graph', 'children'),
           Output('cluster-table', 'children'),
           Output('summary-store', 'data'),
           Output('dropdown_col_1', 'options'),
           Output('dropdown_col_1', 'value'),
           Output('dropdown_col_2', 'options'),
           Output('dropdown_col_2', 'value')],
          [Input('pareto-store', 'data')])
def populate_pareto_front(pareto_store):

    dynamic_plots = []
    summary_store = {}

    metrics = list(pareto_store.keys())

    ps_np = pareto_store.values()
    ps_np = list(ps_np)
    ps_np = np.array(ps_np).T

    # If plot folder does not exist, create it
    if not os.path.exists("plots"):
        os.makedirs("plots")

    if len(ps_np) == 0:
        raise PreventUpdate

    num_samples, num_metrics = ps_np.shape

    if num_samples <= 2:
        raise PreventUpdate

    optimal_k_max = 10
    if num_samples < optimal_k_max:
        optimal_k_max = num_samples

    k_ = optimal_k(ps_np, optimal_k_max)
    km = KMeans(n_clusters=k_, init='random', n_init=10, max_iter=300,  tol=1e-04, random_state=0)
    clusters = km.fit_predict(ps_np)
    
    cluster_names = ['A','B','C','D','E','F','G','H','I','J','K','L']
    cluster_names = cluster_names[:k_]

    viz_metrics = list(pareto_store.keys())
    viz_metrics = [metric.replace("_", " ") for metric in viz_metrics]
    df = pd.DataFrame(km.cluster_centers_, columns=viz_metrics)
    df_tmp = pd.DataFrame({'Cluster Names': cluster_names})
    df = df_tmp.join(df)
    df = df.round(2)
    
    param_names, param_data = get_param_history("dakota_data.dat")
    closest, _ = pairwise_distances_argmin_min(km.cluster_centers_, ps_np)

    cluster_table = html.Div(children=[dash_table.DataTable(id="cluster-table",
                                                   columns=[{"name": i, "id": i} for i in df.columns],
                                                   data=df.to_dict("records"),
                                                   row_selectable=False,
                                                   row_deletable=False,
                                                   editable=False,
                                                   filter_action="native",
                                                   sort_action="native",
                                                   style_table={"overflowX": "auto"},
                                                   style_cell={'textAlign': 'center'})])

    if num_metrics == 1:
        fig = px.scatter(x=np.arange(0, len(pareto_store[metrics[0]])), y=pareto_store[metrics[0]], title="Automatic")
        show_metric = metrics[0].replace("_"," ")
        fig_title = f"{show_metric} Metric Performance"
        fig.update_layout(xaxis_title="Iteration", yaxis_title=f"{show_metric}", title={'text': fig_title,'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        fig.update(layout_coloraxis_showscale=False)
        dynamic_plots.append(dcc.Graph(id='pareto-graph',figure=fig))
    elif num_metrics == 2:
        clusters = list(clusters)
        clusters = [str(x) for x in clusters]
        clusters = [x.replace(x, cluster_names[int(x)]) for x in clusters]
        clusters = np.asarray(clusters)

        # Make centroids a little bigger than the other points
        size = np.zeros([len(clusters)])
        size[:] = 1
        for centroid in closest:
            size[centroid] = 5

        df_np = np.column_stack([clusters, size, pareto_store[metrics[0]], pareto_store[metrics[1]]])
        df = pd.DataFrame(df_np, columns=['clusters','size', f'{metrics[0]}', f'{metrics[1]}']) 
        df = df.astype({'clusters': str, 'size':float, f'{metrics[0]}': float, f'{metrics[1]}': float})

        fig = px.scatter(df, x=f"{metrics[0]}", y=f"{metrics[1]}", color='clusters', size='size', title="Automatic", category_orders={'clusters': np.sort(df['clusters'].unique())})
        metric_x = metrics[0].replace("_"," ")
        metric_y = metrics[1].replace("_"," ")
        fig_title = f"{metric_x} vs. {metric_y}"
        fig.update_layout(xaxis_title=f"{metric_x}", yaxis_title=f"{metric_y}", title={'text': fig_title,'y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        fig.update(layout_coloraxis_showscale=False)
        dynamic_plots.append(dcc.Graph(id='pareto-graph',figure=fig))
        fig.write_image("plots/centroids.png")
    else:
        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(ps_np)

        clusters = list(clusters)
        clusters = [str(x) for x in clusters]
        clusters = [x.replace(x, cluster_names[int(x)]) for x in clusters]
        clusters = np.asarray(clusters)

        # Make centroids a little bigger than the other points
        size = np.zeros([len(clusters)])
        size[:]= 1
        for centroid in closest:
            size[centroid] = 5

        df_np = np.column_stack([clusters, size, pca_features])
        df = pd.DataFrame(df_np, columns=['clusters','size', 'PCA 0', 'PCA 1']) 
        df = df.astype({'clusters': str, 'size':float, 'PCA 0': float, 'PCA 1': float})

        fig = px.scatter(df, x='PCA 0', y='PCA 1', color='clusters', size='size', title="Automatic", category_orders={'clusters': np.sort(df['clusters'].unique())})
        fig.update_layout(xaxis_title=f"PCA 0", yaxis_title=f"PCA 1", title={'text': 'PCA Summarized Pareto Front','y':0.85,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        dynamic_plots.append(dcc.Graph(id='pareto-graph',figure=fig))
        fig.write_image("plots/centroids.png")

    summary_store["param_names"] = param_names
    summary_store["param_data"] = param_data
    summary_store["closest"] = closest
    summary_store["cluster_names"] = cluster_names
    summary_store["metrics_data"] = ps_np
    summary_store["metrics_names"] = viz_metrics
    
    return dynamic_plots, cluster_table, summary_store, cluster_names,  cluster_names[0], cluster_names, cluster_names[1]


@callback(
    [Output('analysis_col_1', 'children'),
     Output('analysis_col_2', 'children')],
    [Input('summary-store', 'data'),
     Input('experiments-store', 'data'),
     Input('dropdown_col_1', 'value'),
     Input('dropdown_col_2', 'value')],
    prevent_initial_call=True,
)
def update_analysis_cols(summary_store, experiments_store, dropdown_1, dropdown_2):

    ac_col_1_dropdown = generate_pdf_report(summary_store, experiments_store, dropdown_1, 'DECISION_Summary_Report_1.pdf')

    ac_col_2_dropdown = generate_pdf_report(summary_store, experiments_store, dropdown_2, 'DECISION_Summary_Report_2.pdf')

    return ac_col_1_dropdown, ac_col_2_dropdown


@callback(
    Output("download-button-1", "data"),
    [Input("button-1", "n_clicks")],
    prevent_initial_call=True,
)
def download_selected_config_1(n_clicks):

    input_file = "DECISION_Summary_Report_1.pdf"
    output_file = "DECISION_Summary_Report.pdf"
    shutil.copy(input_file, output_file)
    return send_file(output_file)


@callback(
    Output("download-button-2", "data"),
    Input("button-2", "n_clicks"),
    prevent_initial_call=True,
)
def download_selected_config_2(n_clicks):

    input_file = "DECISION_Summary_Report_2.pdf"
    output_file = "DECISION_Summary_Report.pdf"
    shutil.copy(input_file, output_file)
    return send_file(output_file)






