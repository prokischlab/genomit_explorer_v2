import dash
from dash import html, dcc

dash.register_page(__name__, path='/', order=0)

layout = html.Div(children=[
    html.Div([
        html.H1(children='GENOMITexplorer'),
        html.Br(),
        html.P(
            'GENOMITexplorer is an open access online resource created as part of the study '
            '“Diagnosing pediatric mitochondrial disease by exome sequencing: lessons from 2,000 suspected cases” '
            'by Stenton et al., (in submission) led by Dr. Holger Prokisch at the Technical University of Munich. '
            'It is the result of an international collaboration initiated '
            'by the European Network for Mitochondrial Diseases (GENOMIT).'),
        html.P([
            html.A('GENOMIT', href='https://genomit.eu/', target="_blank"),
            ' is an E-Rare funded network of partners at established national hubs for the '
            'biochemical diagnosis, genetic diagnosis, and care of patients with mitochondriopathies acting '
            'in close collaboration with mitochondrial disease patient organizations to improve the diagnosis '
            'and care of mitochondrial disease patients.'
        ]),
        html.P([
            'All clinicians and researchers contributing data to GENOMITexplorer or involved in the creation '
            'of the resource are acknowledged ', html.A('here', href='/contributors'), '.'
        ]),

        html.P('The resource contains:'),

        html.P(html.B(['1) Information on the variant-level for all “pathogenic” and “likely pathogenic” '
                       'variants reported across >1,000 patients in the ',
                       html.A('GENOMIT exome study',
                              href='https://www.medrxiv.org/content/10.1101/2021.06.21.21259171v1.full',
                              target="_blank"),
                       ' and >200 patients in the ',
                       html.A('Leigh syndrome study',
                              href='https://onlinelibrary.wiley.com/doi/abs/10.1002/ana.26313', target="_blank"),
                       ' by the Beijing Leigh Group Project.'])),
        html.P('Variants are listed with their respective predicted function, heteroplasmy level '
               '(for mitochondrial DNA variants), allele frequency (according to gnomAD), CADD score, SIFT score, '
               'ACMG classification, functional evidence, and phenotype semantic similarity score.'),

        html.P(html.B(['2) Information on HPO-gene associations, on the ',
                       html.A('patient-level', href='/patient_level'),
                       ' (>7,500 patients) and ',
                       html.A('gene-level', href='/gene_level'),
                       ' (>450 genes).'])),
        html.P('HPO-gene association are provided for all patients included in the exome study (>2,000) in addition '
               'to molecularly diagnosed patients from mitochondrial disease registries (mitoNET and Besta, >1,000), '
               'from the Beijing Leigh Group Project (>200), and from literature reports (>4,500). '
               'For mtDNA encoded diagnoses, associations are provided on the variant level.'),
        html.P('The most discriminating phenotypes by molecular diagnosis can be explored for all genes '
               'with ≥5 reported patients carrying “pathogenic” and “likely pathogenic” variants.'),
        html.P(['Contact: prokisch@helmholtz-muenchen.de'])
    ], style={"margin-left": "10%", "margin-right": "10%"})
])
