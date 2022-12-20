import dash
from dash import html, dcc, dash_table, callback, Input, Output
import pandas as pd
import json

dash.register_page(__name__, path='/gene_level', order=1)

df_gene_level = pd.read_csv('data/precalc_data/gene_level.csv')
with open('data/precalc_data/meta_data.json') as f:
    meta_data = json.load(f)
gene_names = meta_data['gene_names']
gene_names.remove('Unsolved')
hpo_terms = meta_data['hpo_terms']

def perc_str(a, b):
    perc = a / b
    perc = round(perc * 100)
    return f'{a}/{b} ({perc}%)'

def prepare_df_visualise(df: pd.DataFrame):
    df_res = df.copy()

    df_res['patients_gene'] = df_res.apply(lambda row: perc_str(row.gene_hpo, row.gene_total), axis=1)
    df_res['patients_total'] = df_res.apply(lambda row: perc_str(row.all_patients_hpo, row.all_patients), axis=1)

    df_res = df_res.reset_index(drop=True)
    df_res = df_res.reset_index()
    df_res['index'] += 1

    df_res = \
        df_res[['gene_name', 'HPO_ID', 'HPO_term', 'patients_gene', 'patients_total', 'odds_ratio', 'p_val']]
    df_res = df_res.sort_values('p_val')

    df_res['odds_ratio'] = df_res['odds_ratio'].apply(lambda row: '{:.2f}'.format(row))
    df_res['p_val'] = df_res['p_val'].apply(lambda row: '{:.2E}'.format(row))

    df_res.columns = \
        ['Gene name', 'HPO ID', 'HPO term', 'Patients with this genetic diagnosis and HPO term',
         'All other patients with this HPO', 'Odds ratio', 'P value']
    return df_res

layout = html.Div(children=[
    html.H1(children='Gene-level HPO associations'),
    html.Br(),
    html.H3(children='Filtration:'),
    html.Div([
        html.Div([
            'Select gene:',
            dcc.Dropdown(gene_names, id='gene-dropdown')
        ], style={"width": "20%", 'display': 'inline-block'}),
        html.Div([
            'Select HPOs:',
            dcc.Dropdown(list(hpo_terms.keys()), id='hpo-dropdown', multi=True)
        ], style={"width": "60%", 'display': 'inline-block', "margin-left": "15px"}),
    ]),
    html.Br(),
    dash_table.DataTable(prepare_df_visualise(df_gene_level).to_dict('records'), id='gene-table', page_size=10),
    html.H3(children='Combine HPOs:'),
    html.Br(),
])


@callback(
    Output('gene-table', 'data'),
    Input('gene-dropdown', 'value'),
    Input('hpo-dropdown', 'value'),
)
def filter_table(gene_name, hpos):
    df_res = df_gene_level.copy()

    if gene_name is not None:
        df_res = df_res[df_res.gene_name == gene_name]

    if hpos is not None and len(hpos) > 0:
        hpo_ids = [hpo_terms[h][0] for h in hpos]
        df_res = df_res[df_res.HPO_ID.isin(hpo_ids)]

    return prepare_df_visualise(df_res).to_dict('records')
