import dash
from dash import html, dcc, dash_table, callback, Input, Output
import pandas as pd
from scipy.stats import fisher_exact
import json

dash.register_page(__name__, path='/')

df_all = pd.read_csv('data/precalc_data/data_all.csv')
df_all.loc[df_all.gene_name == '.', 'gene_name'] = 'Unsolved'

with open('data/precalc_data/meta_data.json') as f:
    meta_data = json.load(f)
gene_names = meta_data['gene_names']
gene_names.remove('Unsolved')
hpo_terms = meta_data['hpo_terms']

gene_patient_num = \
    df_all.groupby(['gene_name', 'exome_ID']).count().reset_index().groupby(['gene_name']).count().exome_ID
hpo_patient_num = \
    df_all.groupby(['HPO_ID', 'exome_ID']).count().reset_index().groupby(['HPO_ID']).count().exome_ID


df_filter = df_all[['gene_name', 'HPO_ID', 'HPO_term', 'exome_ID']].copy()
df_filter = df_filter.groupby(['gene_name', 'HPO_ID', 'exome_ID']).agg({'HPO_term': 'first'}).reset_index()\
    .groupby(['gene_name', 'HPO_ID']).agg({'HPO_term': 'first', 'exome_ID': 'count'}).reset_index()


def perc_str(a, b):
    perc = a / b
    perc = round(perc * 100)
    return f'{a}/{b} ({perc}%)'


total_patient_num = len(df_all.exome_ID.unique())

df_filter['this_gene_hpo'] = \
    df_filter.apply(lambda row: perc_str(row.exome_ID, gene_patient_num[row.gene_name]), axis=1)
df_filter['all_patients_hpo'] = \
    df_filter.apply(lambda row: perc_str(hpo_patient_num[row.HPO_ID], total_patient_num), axis=1)

# df_filter['fisher_res'] = \
#     df_filter.apply(lambda row: fisher_exact([[row.exome_ID, gene_patient_num[row.gene_name] - row.exome_ID],
#                                               [hpo_patient_num[row.HPO_ID], total_patient_num -
#                                                hpo_patient_num[row.HPO_ID]]]), axis=1)
# df_filter['fisher_res'] = df_filter['fisher_res'].apply(lambda row: ','.join([str(row[0]), str(row[1])]))

df_filter = df_filter[['gene_name', 'HPO_ID', 'HPO_term', 'this_gene_hpo', 'all_patients_hpo']]

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
    dash_table.DataTable(df_filter.to_dict('records'), id='gene-table', page_size=10),
    html.H3(children='Combine HPOs:'),
    html.Br(),
])


@callback(
    Output('gene-table', 'data'),
    Input('gene-dropdown', 'value'),
    Input('hpo-dropdown', 'value'),
)
def filter_table(gene_name, hpos):
    df_res = df_filter.copy()

    if gene_name is not None:
        df_res = df_res[df_res.gene_name == gene_name]

    if hpos is not None and len(hpos) > 0:
        hpo_ids = [hpo_terms[h][0] for h in hpos]
        df_res = df_res[df_res.HPO_ID.isin(hpo_ids)]

    return df_res.to_dict('records')
