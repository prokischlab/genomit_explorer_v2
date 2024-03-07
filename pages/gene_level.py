import dash
from dash import html, dcc, dash_table, callback, Input, Output
from dash.dash_table.Format import Format, Scheme
import dash_daq as daq
import dash_bootstrap_components as dbc
import pandas as pd
import json
from scipy.stats import fisher_exact

dash.register_page(__name__, path='/gene_level', order=1)

df_gene_level = pd.read_csv('data/precalc_data/gene_level.csv')
with open('data/precalc_data/meta_data.json') as f:
    meta_data = json.load(f)
gene_names = meta_data['gene_names']
# gene_names.remove('Unsolved')
hpo_terms = meta_data['hpo_terms']

df_all = pd.read_csv('data/precalc_data/data_all.csv')


def perc_str(a, b):
    perc = a / b
    perc = round(perc * 100)
    return f'{a}/{b} ({perc}%)'


def prepare_df_visualise(df: pd.DataFrame):
    df_res = df.copy()

    df_res['patients_gene'] = None
    df_res['patients_total'] = None

    if df_res.size > 0:
        df_res['patients_gene'] = df_res.apply(lambda row: perc_str(row.gene_hpo, row.gene_total), axis=1)
        df_res['patients_total'] = df_res.apply(lambda row: perc_str(row.all_patients_hpo, row.all_patients), axis=1)

    df_res = df_res.reset_index(drop=True)
    df_res = df_res.reset_index()
    df_res['index'] += 1

    df_res = \
        df_res[['gene_name', 'HPO_ID', 'HPO_term', 'patients_gene', 'patients_total', 'odds_ratio', 'p_val']]
    df_res = df_res.sort_values('p_val')

    df_res.columns = \
        ['Gene name', 'HPO ID', 'HPO term', 'Patients with this genetic diagnosis and HPO term',
         'All other patients with this HPO', 'Odds ratio', 'P value']
    return df_res


visualise_df = prepare_df_visualise(df_gene_level)
visualise_columns = []
for col in visualise_df.columns:
    if col == 'P value':
        visualise_columns.append(
            dict(id=col, name=col, type='numeric', format=Format(precision=2, scheme=Scheme.exponent))
        )
    elif col == 'Odds ratio':
        visualise_columns.append(
            dict(id=col, name=col, type='numeric', format=Format(precision=2, scheme=Scheme.decimal))
        )
    else:
        visualise_columns.append({'name': col, 'id': col})

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
        ], style={"width": "50%", 'display': 'inline-block', "margin-left": "15px"}),
    ]),
    html.Br(),
    html.Div([
        html.Div([
            'Nuclear / MT:',
            dbc.RadioItems(options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Nuclear', 'value': 'nuclear'},
                {'label': 'MT', 'value': 'mt'}
            ], id='nuclear-mt-radio', value='all', inline=True)
        ], style={"width": "20%", 'display': 'inline-block'}),

        html.Div([
            'Significant only:',
            dbc.RadioItems(options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Significant', 'value': 'significant'},
            ], id='significant-switch', value='significant', inline=True),
        ], style={"width": "20%", 'display': 'inline-block', "margin-left": "15px"}),
    ]),
    html.Br(),
    dash_table.DataTable(visualise_df.to_dict('records'), id='gene-table',
                         # page_size=10,
                         page_action='none',
                         virtualization=True,
                         fixed_rows={'headers': True},
                         style_cell={'minWidth': 0, 'width': 0, 'maxWidth': 300},
                         style_table={'height': 400},
                         sort_action="native", sort_mode="multi", columns=visualise_columns, ),
    html.Br(),
    html.H3(children='Combine HPOs:'),
    html.Br(),
    html.Div([
        html.Div([
            html.Div([
                html.Label(children='Gene:'),
                html.Label(children='', id='gene-name', style={'font-weight': 'bold', 'margin-left': '10px'})
            ], style={'display': 'inline-block'}),
            html.Br(),
            html.Div([
                html.Label(children='HPOs:'),
                html.Label(children='', id='hpos', style={'font-weight': 'bold', 'margin-left': '10px'})
            ], style={'display': 'inline-block'}),
            html.Br(),
            html.Div([
                html.Label(children='Patients with this genetic diagnosis and HPO terms combination:'),
                html.Label(children='', id='patients_gene_combine',
                           style={'font-weight': 'bold', 'margin-left': '10px'})
            ], style={'display': 'inline-block'}),
            html.Br(),
            html.Div([
                html.Label(children='All other patients with this HPOs combination:'),
                html.Label(children='', id='patients_combine',
                           style={'font-weight': 'bold', 'margin-left': '10px'})
            ], style={'display': 'inline-block'}),
            html.Br(),
            html.Div([
                html.Label(children='Fisher exact test:'),
                html.Label(children='', id='fisher_result',
                           style={'font-weight': 'bold', 'margin-left': '10px'})
            ], style={'display': 'inline-block'}),
        ], style={'display': 'none'}, id='combine-hpo-div'),
        html.Div([
            html.Label(children='Select gene and HPOs to show combination statistics'),
        ], style={'display': 'block'}, id='combine-hpo-div-empty'),
    ], style={"width": "50%"}),
])


@callback(
    Output('gene-table', 'data'),
    Output('gene-name', 'children'),
    Output('hpos', 'children'),
    Output('patients_gene_combine', 'children'),
    Output('patients_combine', 'children'),
    Output('fisher_result', 'children'),

    Output('combine-hpo-div', 'style'),
    Output('combine-hpo-div-empty', 'style'),
    Input('gene-dropdown', 'value'),
    Input('hpo-dropdown', 'value'),
    Input('nuclear-mt-radio', 'value'),
)
def filter_table(gene_name, hpos, nuclear_mt):
    df_res = df_gene_level.copy()

    show_combine_hpo = True
    hpos_show = ''
    patients_gene_combine = ''
    other_patients_combine = ''
    fisher_result = ''

    if gene_name is not None:
        df_res = df_res[df_res.gene_name == gene_name]
    else:
        show_combine_hpo = False

    hpo_ids = []
    if hpos is not None and len(hpos) > 0:
        hpo_ids = [hpo_terms[h][0] for h in hpos]
        df_res = df_res[df_res.HPO_ID.isin(hpo_ids)]
    else:
        show_combine_hpo = False

    if show_combine_hpo:
        combine_hpo_div_style = {'display': 'block'}
        combine_hpo_div_empty_style = {'display': 'none'}
        hpos_show = ', '.join(hpo_ids)

        df_hpo_comb = df_all[df_all.gene_name == gene_name].groupby('exome_ID')['HPO_ID'].apply(list)
        df_hpo_comb = df_hpo_comb.apply(lambda row: set(hpo_ids).issubset(set(row)))
        patients_with_gene_hpos = df_hpo_comb.sum()
        patients_with_gene = df_hpo_comb.size
        patients_gene_combine = perc_str(patients_with_gene_hpos, patients_with_gene)

        df_hpo_comb = df_all[~(df_all.gene_name == gene_name)].groupby('exome_ID')['HPO_ID'].apply(list)
        df_hpo_comb = df_hpo_comb.apply(lambda row: set(hpo_ids).issubset(set(row)))
        other_patients_with_hpos = df_hpo_comb.sum()
        other_patients = df_hpo_comb.size
        other_patients_combine = perc_str(other_patients_with_hpos, other_patients)

        fisher_res = fisher_exact([[patients_with_gene_hpos, patients_with_gene - patients_with_gene_hpos],
                                   [other_patients_with_hpos, other_patients - other_patients_with_hpos]])
        fisher_result = 'odds ratio: {:.2f}, p-value: {:.2e}'.format(fisher_res[0], fisher_res[1])
    else:
        combine_hpo_div_style = {'display': 'none'}
        combine_hpo_div_empty_style = {'display': 'block'}

    if nuclear_mt == 'nuclear':
        df_res = df_res[~df_res.gene_name.str.startswith('MT-')]
    elif nuclear_mt == 'mt':
        df_res = df_res[df_res.gene_name.str.startswith('MT-')]

    return prepare_df_visualise(df_res).to_dict('records'), gene_name, hpos_show, \
        patients_gene_combine, other_patients_combine, fisher_result, \
        combine_hpo_div_style, combine_hpo_div_empty_style
