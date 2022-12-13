import os
import shutil
import pandas as pd
import json


def precalc(data_dir, file_name):
    df_all = pd.read_csv(os.path.join(data_dir, file_name), sep='\t')
    precalc_dir = os.path.join(data_dir, 'precalc_data')
    recalc = False

    if os.path.isdir(precalc_dir):
        df_recalc = pd.read_csv(os.path.join(precalc_dir, 'data_all.csv'))
        if df_all.size != df_recalc.size:
            shutil.rmtree(precalc_dir)
            recalc = True
    else:
        recalc = True

    if recalc:
        print('Recalc')
        df_all.loc[df_all.gene_name == '.', 'gene_name'] = 'Unsolved'

        gene_names = df_all.gene_name
        gene_names = gene_names.unique()
        gene_names.sort()
        gene_names = gene_names.tolist()

        patients_ids = df_all.exome_ID
        patients_ids = patients_ids.unique()
        patients_ids.sort()
        patients_ids = patients_ids.tolist()

        hpo_terms = df_all[['HPO_ID', 'HPO_term']].drop_duplicates(subset=['HPO_ID'])
        hpo_terms = hpo_terms.sort_values('HPO_ID')
        hpo_terms = {
            row['HPO_ID'] + ', ' + row['HPO_term']: (row['HPO_ID'], row['HPO_term']) for i, row in hpo_terms.iterrows()
        }

        os.makedirs(precalc_dir)

        meta_data = {
            'gene_names': gene_names,
            'hpo_terms': hpo_terms,
            'patients_ids': patients_ids
        }

        df_all.to_csv(os.path.join(precalc_dir, 'data_all.csv'), index=False)
        with open(os.path.join(precalc_dir, 'meta_data.json'), 'w') as f:
            json.dump(meta_data, f)
