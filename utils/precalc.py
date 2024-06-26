import os
import shutil
import pandas as pd
import json
import logging
from scipy.stats import fisher_exact
from tqdm import tqdm


def precalc(data_dir, file_name):
    df_all = pd.read_csv(os.path.join(data_dir, file_name), sep='\t')
    # df_all = pd.read_csv(os.path.join(data_dir, file_name), sep=',')
    # df_all = df_all[df_all.mito_gene == True]
    precalc_dir = os.path.join(data_dir, 'precalc_data')

    study_id = pd.read_csv(os.path.join(data_dir, 'study_ID.txt'), sep='\t')
    study_id['exome_ID'] = study_id['exome_ID'].str.strip()
    study_id['study_ID'] = study_id['study_ID'].str.strip()
    # study_id = study_id.set_index('exome_ID')
    # study_id_dict = study_id.to_dict()['study_ID']
    #
    # df_all['exome_ID_temp'] = df_all['exome_ID'].str.strip().map(study_id_dict)
    # df_all.loc[df_all['exome_ID_temp'].notna(), 'exome_ID'] = df_all['exome_ID_temp']

    recalc_data_all = False

    data_all_path = os.path.join(precalc_dir, 'data_all.csv')
    meta_data_path = os.path.join(precalc_dir, 'meta_data.json')
    gene_level_path = os.path.join(precalc_dir, 'gene_level.csv')
    hpo_level_path = os.path.join(precalc_dir, 'hpo_level.csv')

    if os.path.isdir(precalc_dir):
        if not os.path.exists(data_all_path) or \
                not os.path.exists(meta_data_path) or \
                not os.path.exists(gene_level_path) or \
                not os.path.exists(hpo_level_path):
            shutil.rmtree(precalc_dir)
            recalc_data_all = True
        else:
            df_recalc = pd.read_csv(data_all_path)
            if df_all.size != df_recalc.size:
                shutil.rmtree(precalc_dir)
                recalc_data_all = True
    else:
        recalc_data_all = True

    if recalc_data_all:
        logging.info('Recalc data all')
        os.makedirs(precalc_dir)

        df_all.loc[df_all.gene_name == '.', 'gene_name'] = 'Unsolved'

        gene_names = df_all.gene_name
        gene_names = gene_names.unique()
        gene_names.sort()
        gene_names = gene_names.tolist()

        patients_ids = df_all.exome_ID.astype(str)
        patients_ids = patients_ids.unique()
        patients_ids.sort()
        patients_ids = patients_ids.tolist()

        hpo_terms = df_all[['HPO_ID', 'HPO_term']].drop_duplicates(subset=['HPO_ID'])
        hpo_terms = hpo_terms.sort_values('HPO_ID')
        hpo_terms = {
            row['HPO_ID'] + ', ' + row['HPO_term']: (row['HPO_ID'], row['HPO_term']) for i, row in hpo_terms.iterrows()
        }

        meta_data = {
            'gene_names': gene_names,
            'hpo_terms': hpo_terms,
            'patients_ids': patients_ids
        }

        logging.info('Recalc gene level data')
        df_gene_level = df_all.copy()

        gene_patient_num = \
            df_gene_level.groupby(['gene_name', 'exome_ID'])\
                .count().reset_index().groupby(['gene_name']).count().exome_ID
        hpo_patient_num = \
            df_gene_level.groupby(['HPO_ID', 'exome_ID'])\
                .count().reset_index().groupby(['HPO_ID']).count().exome_ID

        df_gene_level = df_gene_level[['gene_name', 'HPO_ID', 'HPO_term', 'exome_ID']]
        df_gene_level = df_gene_level.groupby(['gene_name', 'HPO_ID', 'exome_ID'])\
            .agg({'HPO_term': 'first'}).reset_index()\
            .groupby(['gene_name', 'HPO_ID']).agg({'HPO_term': 'first', 'exome_ID': 'count'}).reset_index()

        total_patient_num = len(df_all.exome_ID.unique())

        tqdm.pandas()

        df_gene_level['gene_hpo'] = df_gene_level.exome_ID
        df_gene_level['gene_total'] = df_gene_level.progress_apply(lambda row: gene_patient_num[row.gene_name], axis=1)
        df_gene_level['all_patients_hpo'] = df_gene_level.progress_apply(lambda row: hpo_patient_num[row.HPO_ID], axis=1)
        df_gene_level['all_patients'] = total_patient_num
        df_gene_level['all_patients_hpo'] = df_gene_level['all_patients_hpo'] - df_gene_level['gene_hpo']
        df_gene_level['all_patients'] = df_gene_level['all_patients'] - df_gene_level['gene_total']
        df_gene_level = df_gene_level[df_gene_level.gene_name != 'Unsolved']
        df_gene_level['fisher_res'] = \
            df_gene_level.progress_apply(lambda row: fisher_exact([[row.gene_hpo, row.gene_total - row.gene_hpo],
                                                          [row.all_patients_hpo,
                                                           row.all_patients - row.all_patients_hpo]]), axis=1)
        df_gene_level['odds_ratio'] = df_gene_level['fisher_res'].progress_apply(lambda row: row[0])
        df_gene_level['p_val'] = df_gene_level['fisher_res'].progress_apply(lambda row: row[1])
        df_gene_level = df_gene_level[['gene_name', 'HPO_ID', 'HPO_term', 'gene_hpo', 'gene_total',
                                       'all_patients_hpo', 'all_patients', 'odds_ratio', 'p_val']]

        df_hpo_level = df_all.copy()
        df_hpo_level = df_hpo_level[['HPO_ID', 'HPO_term', 'gene_name', 'exome_ID']]
        df_hpo_level = df_hpo_level.groupby(['HPO_ID', 'gene_name', 'exome_ID']) \
            .agg({'HPO_term': 'first'}).reset_index() \
            .groupby(['HPO_ID', 'gene_name']).agg({'HPO_term': 'first', 'exome_ID': 'count'}).reset_index()

        logging.info('Save data to file')
        df_all.to_csv(data_all_path, index=False)
        df_gene_level.to_csv(gene_level_path, index=False)
        df_hpo_level.to_csv(hpo_level_path, index=False)
        with open(meta_data_path, 'w') as f:
            json.dump(meta_data, f)
