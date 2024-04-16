import logging

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from utils.precalc import precalc

logging.basicConfig(level=logging.INFO)

# precalc('data', 'exomes2000.HPO.txt')
# precalc('data', 'cohorts_hpo_pat_nikita.csv')
precalc('data', 'GENOMITexplorer.patient_ancestor_HPO.txt')
print('GENOMITexplorer.patient_ancestor_HPO.txt')

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("GENOMITexplorer"),
        html.Hr(),
        # html.P(
        #     "A simple sidebar layout with navigation links", className="lead"
        # ),
        dbc.Nav(
            [
                dbc.NavLink(page['name'], href=page['relative_path'], active="exact")
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
   dash.page_container
], id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([
    sidebar,
    content
])

server = app.server

if __name__ == '__main__':
    app.run_server(debug=False)
