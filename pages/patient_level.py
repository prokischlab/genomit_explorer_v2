import dash
from dash import html, dcc, dash_table, callback, Input, Output
import pandas as pd
import json

dash.register_page(__name__, path='/patient_level', order=3)


def prepare_df_visualise(df: pd.DataFrame):
    df_res = df.copy()
    df_res = df_res[['exome_ID', 'gene_name', 'HPO_ID', 'HPO_term']]
    # df_res.exome_ID = 'MWES' + df_res.exome_ID.str.c
    # df['exome_ID'] = 'MWES' + df['exome_ID'].astype(str)
    # df_res = df_res.reset_index(drop=True)
    # df_res = df_res.reset_index()
    # df_res['index'] += 1
    df_res.columns = ['Patient ID', 'Gene name', 'HPO ID', 'HPO term']
    return df_res


df_all = pd.read_csv('data/precalc_data/data_all.csv')
with open('data/precalc_data/meta_data.json') as f:
    meta_data = json.load(f)
gene_names = meta_data['gene_names']
patients_ids = meta_data['patients_ids']
hpo_terms = meta_data['hpo_terms']

layout = html.Div(children=[
    html.H1(children='Patient-level HPO associations'),
    html.Br(),
    html.P('This searchable table contains the patient-level HPO terms from our WES study (>2,000, prefix “MWES”) '
           'in addition to paediatric molecular confirmed patients from the mitoNET and Besta registries '
           '(>300, prefix “MREG”), paediatric molecular confirmed Leigh syndrome patients from the Beijing Leigh Group '
           'Project (>200, prefix “BLGP”), and paediatric molecular confirmed patients curated from the literature '
           '(>1,500, prefix “MLIT”)'),
    html.Br(),
    html.Div([
        html.Div([
            'Select patients:',
            dcc.Dropdown(patients_ids, id='patients-dropdown', multi=True)
        ], style={"width": "20%", 'display': 'inline-block'}),
        html.Div([
            'Select genes:',
            dcc.Dropdown(gene_names, id='gene-dropdown', multi=True)
        ], style={"width": "20%", 'display': 'inline-block', "margin-left": "15px"}),
        html.Div([
            'Select HPOs:',
            dcc.Dropdown(list(hpo_terms.keys()), id='hpo-dropdown', multi=True)
        ], style={"width": "50%", 'display': 'inline-block', "margin-left": "15px"}),
    ]),
    html.Br(),
    dash_table.DataTable(prepare_df_visualise(df_all).to_dict('records'), id='patient-table',
                         page_size=20,
                         # page_action='none',
                         # virtualization=True,
                         # fixed_rows={'headers': True},
                         # style_cell={'minWidth': 90, 'maxWidth': 300},
                         # style_table={'height': 500},
                         # sort_action="native", sort_mode="multi",
                         ),
    html.Br(),
    html.P([html.B('Interested in patient-level HPO terms for a specific gene?'),
            ' Enter your gene of interest in the search box. '
            'All individuals with a defect in this gene will be returned with their HPO terms.']),
])


@callback(
    Output('patient-table', 'data'),
    Input('patients-dropdown', 'value'),
    Input('gene-dropdown', 'value'),
    Input('hpo-dropdown', 'value'),
)
def filter_table(patients_ids, gene_names, hpos):
    df_res = df_all.copy()

    if patients_ids is not None and len(patients_ids) > 0:
        df_res = df_res[df_res.exome_ID.isin(patients_ids)]

    if gene_names is not None and len(gene_names) > 0:
        df_res = df_res[df_res.gene_name.isin(gene_names)]

    if hpos is not None and len(hpos) > 0:
        hpo_ids = [hpo_terms[h][0] for h in hpos]
        df_res = df_res[df_res.HPO_ID.isin(hpo_ids)]

    return prepare_df_visualise(df_res).to_dict('records')
