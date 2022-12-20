import dash
from dash import html, dcc

dash.register_page(__name__, path='/contributors', order=5)

contributors = []

with open('data/contributors.txt') as f:
    for line in f:
        if line != '':
            contributors.append(line)

layout = html.Div(children=[
    html.Div([
        html.H1(children='Acknowledgment of contribution'),
        html.Br(),
        html.B(
            'The following clinicians and researchers contributed data to GENOMITexplorer '
            'or were involved in the creation:'),
        html.Br(),
        html.Br(),
        html.P([html.P(c) for c in contributors])
    ], style={"margin-left": "10%", "margin-right": "10%"})
])
