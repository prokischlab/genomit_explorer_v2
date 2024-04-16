import dash
from dash import html, dcc, dash_table, callback, Input, Output
import pandas as pd
import json

# dash.register_page(__name__, path='/phenotype_level', order=4)


def prepare_df_visualise(df: pd.DataFrame):
    df_res = df.copy()
    # df_res = df_res[['exome_ID', 'gene_name', 'HPO_ID', 'HPO_term']]
    df_res = df_res[['gene_name', 'number_of_patient']]
    df_res = df_res.reset_index(drop=True)
    df_res = df_res.reset_index()
    df_res['index'] += 1
    # df_res.columns = ['N', 'Patient ID', 'Gene name', 'HPO ID', 'HPO term']
    df_res.columns = ['N', 'Gene name', 'Number of patients']
    return df_res


df_all = pd.read_csv('data/precalc_data/data_all.csv')
df_g = df_all.groupby('exome_ID').agg(
        gene_name=pd.NamedAgg(column='gene_name', aggfunc='first'),
        HPO_ID=pd.NamedAgg(column='HPO_ID', aggfunc=lambda x: ', '.join(x)),
        HPO_term=pd.NamedAgg(column='HPO_term', aggfunc=lambda x: ', '.join(x))
    ).reset_index()
df_g = df_g.groupby('gene_name').agg(
        number_of_patient=pd.NamedAgg(column='exome_ID', aggfunc='count')
    ).reset_index()

with open('data/precalc_data/meta_data.json') as f:
    meta_data = json.load(f)
gene_names = meta_data['gene_names']
patients_ids = meta_data['patients_ids']
hpo_terms = meta_data['hpo_terms']

layout = html.Div(children=[
    html.H1(children='Phenotype-level HPO associations'),
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
    dash_table.DataTable(prepare_df_visualise(df_g).to_dict('records'), id='phenotype-table', page_size=20),
])


@callback(
    Output('phenotype-table', 'data'),
    Input('patients-dropdown', 'value'),
    Input('gene-dropdown', 'value'),
    Input('hpo-dropdown', 'value'),
)
def filter_table(patients_ids, gene_names, hpos):
    df_res = df_all[['exome_ID', 'gene_name', 'HPO_ID', 'HPO_term']].copy()

    if patients_ids is not None and len(patients_ids) > 0:
        df_res = df_res[df_res.exome_ID.isin(patients_ids)]

    if gene_names is not None and len(gene_names) > 0:
        df_res = df_res[df_res.gene_name.isin(gene_names)]

    df_res_g = df_res.groupby('exome_ID')

    if hpos is not None and len(hpos) > 0:
        hpo_ids = [hpo_terms[h][0] for h in hpos]
        df_res_g = df_res_g.filter(lambda x: all(hpo_id in x['HPO_ID'].values for hpo_id in hpo_ids))\
            .groupby('exome_ID')

    df_res_g = df_res_g.agg(
        gene_name=pd.NamedAgg(column='gene_name', aggfunc='first'),
        HPO_ID=pd.NamedAgg(column='HPO_ID', aggfunc=lambda x: ', '.join(x)),
        HPO_term=pd.NamedAgg(column='HPO_term', aggfunc=lambda x: ', '.join(x))
    ).reset_index()
    df_res_g = df_res_g.groupby('gene_name').agg(
        number_of_patient=pd.NamedAgg(column='exome_ID', aggfunc='count')
    ).reset_index()
    return prepare_df_visualise(df_res_g).to_dict('records')
