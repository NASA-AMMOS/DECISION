import dash
import os
import shutil
import logging

from dash  import Dash
from dash  import html
from dash  import dcc
from dash  import Output
from dash  import callback

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

app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id="experiments-store", data={}),
    dcc.Store(id="metrics-store", data={'metrics':[]}),
    dcc.Store(id="parameters-store", data={'parameters':[]}),
    dcc.Store(id="optimizer-store", data={}),
    dcc.Store(id="pareto-store", data={}),
    dcc.Store(id="summary-store", data={}),
    dcc.Store(id="config-store", data={"config_name":"ACME", "config_path":"configs/ACME.yaml"}),

   html.Div(
            className="header-title",
            children=[
                html.Div(
                className="header-logo",
            children=[
                html.Img(src='/assets/DecisionLogo2.png')
                ]),
                ]),
                

    html.Div(
        [
            html.Div(
                className="header-nav-bar",
                children=[
                    html.Div(
                        className="header-nav-bar-buttons",
                        children=[
                dcc.Link(
                    html.Button(f"{page['name']}"), href=page["relative_path"]
                )
                for page in dash.page_registry.values()
                    ]),
            ])
        ]
    ),
    
    dash.page_container
])

if __name__ == '__main__':

    # TODO - put in config during generalization activity
    pickle_procesing_path = "data/ACME_Demo_Data/tmp/"
    rebuild_folder(pickle_procesing_path)
    results_path = "data/ACME_Demo_Data/ACME_preds/"
    rebuild_folder(results_path)

    logging.basicConfig(filename='decision_log.txt', 
                        force=True, 
                        format='%(asctime)s | %(levelname)-7s | %(module)-15s | %(message)s',
                        level=logging.INFO)

    # Clean up old runs if they exists
    if os.path.isfile("dakota.input"):
        logging.info("Removing old dakota.input file")
        os.remove("dakota.input")

    if os.path.isfile("dakota.out"):
        logging.info("Removing old dakota.out file")
        os.remove("dakota.out")

    if os.path.isfile("dakota.rst"):
        logging.info("Removing old dakota.rst file")
        os.remove("dakota.rst")

    app.run_server(debug=True)
