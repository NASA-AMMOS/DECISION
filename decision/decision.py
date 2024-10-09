import dash
import os
import shutil
import logging
import sys

from dash  import Dash
from dash  import html
from dash  import dcc
from dash  import Output
from dash  import callback
from dash  import Input
from dash  import State
from dash  import ALL
from dash.exceptions import PreventUpdate
from dash            import ctx


from pages import home, database, metrics, optimizer, summary, test
from assets import modal_text

import dash_bootstrap_components as dbc

state = {}

def rebuild_folder(dirpath):

    # if old pickle processing directory still exists, remove it.
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)

    # create fresh pickle processing directory 
    # must be clean between sessions since ACME just globs everything in there
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'pages/assets/about.css'
]

app = Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

page_list = ["Task", "Data", "Metrics", "Optimize", "Summary", "Test"]

app.layout = html.Div([
    dcc.Store(id="machine-store", data={'machine': "local"}),
    dcc.Store(id="experiments-store", data={}),
    dcc.Store(id="metrics-store", data={'metrics':[]}),
    dcc.Store(id="parameters-store", data={'parameters':[]}),
    dcc.Store(id="optimizer-store", data={}),
    dcc.Store(id="pareto-store", data={}),
    dcc.Store(id="config-store", data={"config_name":"ACME", "config_path":"configs/ACME.yaml"}),
    dcc.Store(id="run-datetime-store", data={"run_datetime": ""}),
    dcc.Store(id="upload-store", data={}),
    dcc.Store(id='test-image-store', data=[]),
    dcc.Store(id="alerts-store", data=[]), #TODO: Does this need to exist?
    dcc.Store(id="modal-store", data={
        "Parameter Optimization": modal_text.PARAMETER_OPTIMIZATION,
        "Genetic Algorithm Configuration": modal_text.GENETIC_ALGORITHM_CONFIGURATION,
        "Metrics to Optimize": modal_text.METRICS_TO_OPTIMIZE,
        "Experiments to Optimize With": modal_text.EXPERIMENTS_TO_OPTIMIZE_WITH,
        "Optimization Summary": modal_text.OPTIMIZATION_SUMMARY,
        "Configuration Search Space": modal_text.CONFIGURATION_SEARCH_SPACE,
        "Configuration Database": modal_text.CONFIGURATION_DATABASE,
        "Optimization Histograms": modal_text.OPTIMIZATION_HISTOGRAMS,
    }),
    dcc.Store(id="plot-store", data={}),
    dcc.Store(id="cart-store", data={}),
    dcc.Store(id="filtered-table-store", data={}),
    dcc.Store(id="cart-store-loader", data={}),
    dcc.Store(id="test-status", data="standby"),
    dcc.Store(id="genetic-algorithm-config-store", data={
        "max_iterations": { "name": "Maximum Iterations", "description": "Max number of population generations to create and test. Will have a substantial impact on runtime. More iterations will likely improve results but translate into a longer runtime.", "min": 0, "max": 1000, "step": 1, "default": 10 },
        "max_function_evaluations": { "name": "Maximum Function Evaluations", "description": "Max number of individual evaluations (of the objective function on population members). Can be used as a simple stopping criterion, though typically it's better to set this large and rely on other termination conditions. May have an impact runtime depending on other stopping criteria.", "min": 0, "max": 100000, "step": 100, "default": 10000 },
        "population_size": { "name": "Population Size", "description": "Initial number of individuals in the population. Note that the population may wax/wane as the optimization iterations progress. Large values will more thoroughly test the optimization space but increase runtime.", "min": 0, "max": 1000, "step": 1, "default": 50 },
        "mutation_rate": { "name": "Mutation Rate", "description": "Determines how likely it is for mutations to occur. This variable effects the mutation types differently.", "min": 0, "max": 1.0, "step": 0.01, "default": 0.08 },
        "crossover_rate": { "name": "Crossover Rate", "description": "Determines how fast crossovers occur when combining parents information to create an offspring. The total number of crossovers is equal to the crossover_rate * population_size.", "min": 0, "max": 1.0, "step": 0.01, "default": 0.8 },
    }),
    dcc.Store(id='config-search-space-raw', data={}),
    dcc.Store(id='config-search-space-filtered', data={}),

    dcc.Location(id='url', refresh=False),
    
    html.Div(
        children = [
                    html.Div(
                        id="nav-bar-container",
                        children=[]) 
            ,]),
    html.Div(id='home-content', className="hidden", children = [home.layout]),
    html.Div(id='database-content', className="hidden",  children = [database.layout]),
    html.Div(id='metrics-content', className="hidden",  children = [metrics.layout]),
    html.Div(id='optimizer-content', className="hidden", children = [optimizer.layout]),
    html.Div(id='summary-content', className="hidden",  children = [summary.layout]),
    html.Div(id='test-content', className="hidden",  children = [test.layout]),
    html.Div(id='global-alerts', children = []),
    dbc.Modal(id="modal", is_open=False, children=[
        dbc.ModalHeader(dbc.ModalTitle(id="modal-header")),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close-modal", className="ms-auto", n_clicks=0
            )
        ),
    ]),
])

@callback([
           Output('nav-bar-container', 'children'),
           Output('home-content', 'className'),
           Output('database-content', 'className'),
           Output('metrics-content', 'className'),
           Output('optimizer-content', 'className'),
           Output('summary-content', 'className'),
           Output('test-content', 'className')]
           , Input('url', 'pathname'))
def display_page(pathname):
    navbar = get_navbar_layout(pathname)

    class_list = ["hidden"]*len(page_list)

    if pathname == "/" or pathname == "/task":
        class_list[0] = "show"
    else:
        class_list[page_list.index(pathname[1:].capitalize())] = "show"
    
    return navbar, *class_list

def get_navbar_layout(cur_page):
    nav_buttons = []
    nav_header_buttons = []

    first_page = "/" + page_list[0].lower()
    last_page = "/" + page_list[-1].lower()

    if cur_page == "/":
        cur_page = first_page

    if cur_page != first_page:
        previous_page = "/" + page_list[page_list.index(cur_page[1:].capitalize()) - 1].lower()
        nav_buttons.append(dcc.Link(
             dbc.Button("Back", outline=False, color="secondary", size='md'), href=previous_page
                        ))
    else: 
        nav_buttons.append(
             dbc.Button("Back", outline=False, color="secondary", size='md', style = {"visibility": "hidden"})
                        )

    for pg_idx, page in enumerate(page_list):
        if pg_idx <= page_list.index(cur_page[1:].capitalize()):
            link_classes = "form-stepper-completed-line form-stepper-completed text-center form-stepper-list"

            if pg_idx == page_list.index(cur_page[1:].capitalize()):
                link_classes = "form-stepper-completed text-center form-stepper-list"

            nav_header_buttons.append(
            html.Li([
                dcc.Link(html.A([
                        html.H3(f"{page}", className = "label")], className = ""),
            href="/"+page.lower())], className = link_classes))
        else:
            nav_header_buttons.append(
            html.Li([
                dcc.Link(html.A([
                        html.H3(f"{page}", className = "label")], className = ""),
            href="/"+page.lower())], className =  "form-stepper text-center form-stepper-list"))

    if cur_page != last_page:
        next_page = "/" + page_list[page_list.index(cur_page[1:].capitalize()) + 1].lower()
        nav_buttons.append(
            dcc.Link(
                        dbc.Button("Next", outline=False, className= "next-button", color="secondary", size='md'), href=next_page
                    ))
    else:
        nav_buttons.append(
             dbc.Button("Next", outline=False, color="secondary", size='md', style = {"visibility": "hidden"})
                        )

    return html.Div(
                className="header-nav-bar",
                children=[nav_buttons[0], 
        html.Ul(nav_header_buttons, className = "form-stepper form-stepper-horizontal text-center mx-auto pl-0"), nav_buttons[1]])

@callback([Output('modal-header', 'children'),
           Output('modal-body', 'children'),
           Output('modal', 'is_open')],
           Input({"type": "modal-button", "name": ALL}, "n_clicks"),
           Input("close-modal", "n_clicks"),
           State('modal-store', 'data')
)
def toggle_modal(open_modal, close_modal, modal_store):
    if not any(open_modal) or ctx.triggered_id == None:
        raise PreventUpdate
    if ctx.triggered_id == "close-modal":
        return "", "", False
    modal_header = ctx.triggered_id['name']
    modal_body = modal_store[modal_header]
    return modal_header, modal_body, True


@callback(
    Output('global-alerts', 'children', allow_duplicate=True),
    Output('alerts-store', 'data'),
    Input("checklist", "value"),
    Input('table', 'derived_virtual_selected_rows'),
    State("alerts-store", "data"),
    prevent_initial_call=True
)
def callback(metrics, selected_experiments, alerts_store,):

    alerts_list = {
        "need_more_metrics": dbc.Alert("Please select at least two metrics to optimize over", color="danger"),
        "too_many_metrics": dbc.Alert("Be careful adding too many metrics, this can degrade overall performance.", color="warning", dismissable = True),
        "need_one_observation": dbc.Alert("Please select at least one observation to optimize with", color="danger")
    }

    new_alerts = []

    # if metrics are not yet populated do not continue
    if metrics is not None:
        # if no metrics are selected, provide a danger alert
        if len(metrics) < 2:
            new_alerts.append("need_more_metrics")
        # if 4 or more metrics are selected, provide warning
        elif len(metrics) >= 4:
            new_alerts.append("too_many_metrics")

    if selected_experiments is None or selected_experiments == []:
        new_alerts.append("need_one_observation")

    global_alerts = []

    for alert in alerts_store:
        if alert not in new_alerts:
            alerts_store.remove(alert)

    for alert in new_alerts:
        if alert not in alerts_store:
            alerts_store.append(alert)

    for alert in alerts_store:
        global_alerts.append(alerts_list[alert])
   
    return global_alerts, alerts_store

if __name__ == '__main__':

    # TODO - put in config during generalization activity
    pickle_procesing_path = "data/ACME_Demo_Data/tmp/"
    rebuild_folder(pickle_procesing_path)

    logging.basicConfig(filename='decision_log.txt', 
                        force=True, 
                        format='%(asctime)s | %(levelname)-7s | %(module)-15s | %(message)s',
                        level=logging.INFO)

    app.run_server(debug=True)
