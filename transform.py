import pandas as pd
import re
from collections import defaultdict

"""
clean_data performs the following actions:
    - Replacing 'nan' strings with actual null values
    - Renaming scientific_title to title in order to have the same column names in pubmed and clinical_trials data
    - Removing duplicates based on title for pubmed and clinical_trials and based on atccode for drugs
    - Removing empty strings in title (+trailing and leanding whitespaces)
    - Converting dates to one unique format (dd/mm/YYYY)

    Args:
    input_df: pandas.DataFrame

generated_graph creates a json graph to model relations between drugs and journals based on publications from
PubMed and clinical trials
    Args:
    in_df_clinical_trials: pd.DataFrame corresponds to clinical trials data
    in_df_pubmed: pd.DataFrame corresponds to PubMed data
    in_df_drugs: pd.DataFrame corresponds to drugs data

"""
def clean_data(input_df:pd.DataFrame):
    # Replace 'nan' strings with actual NaN values (useful for finding and filling missing values later)
    for c in input_df.columns:
        input_df.loc[input_df[c] == 'nan', [c]] = None
    # Rename scientific_title to title in order to have the same column name in both dataframes (clinical_tirals and pubmed)
    if 'scientific_title' in input_df.columns:
        input_df.rename(columns={"scientific_title": "title"}, inplace=True)

    # Remove leading and trailing whitespaces and remove empty 'title' strings (len < 3)
    # Also remove duplicates based on title as the id can be null
    if 'title' in input_df.columns:
        input_df.drop_duplicates('title', inplace=True)
        input_df.title = input_df.title.apply(lambda x: x.strip())
        input_df.drop( input_df[input_df.title.map(len) < 3 ].index, inplace=True )
        # Remove undecoded utf-8 chars using regex
        input_df['title'] = input_df.title.apply(lambda x: re.sub('\\\\.*(\s|$)', '', x))
        # lowercase
        input_df.title = input_df.title.apply(lambda x: x.lower())
        # And finally convert all dates to one uniform format (dd/mm/YYYY)
        input_df.date = input_df.date.apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))


    # As for drugs data 'atccode' is the identifier and no anomalies have been observed so we can use it to remove duplicates
    else:
        input_df.drop_duplicates('atccode', inplace=True)
        input_df.drug = input_df.drug.apply(lambda x: x.strip()\
                                            .lower())
    return input_df
def generate_graph(in_df_clinical_trials:pd.DataFrame, in_df_pubmed:pd.DataFrame, in_df_drugs:pd.DataFrame):
    # Initialize results list
    results = []
    # Create a set of drugs to avoid duplicates
    drugs_list = set(in_df_drugs['drug'])

    # Iterate over drugs
    for drug in drugs_list:
        drug_info = {
            'drug': drug,
            'journals': []
        }
        # Init a dict for jounals
        journals_dict = {}

        # look into pubmed
        for _, row in in_df_pubmed.iterrows():
            if drug in row['title'].lower():
                journal_key = (row['journal'], row['date'])
                if journal_key not in journals_dict:
                    journals_dict[journal_key] = {
                        'title': row['journal'],
                        'date': row['date'],
                        'pubmed': []
                    }
                journals_dict[journal_key]['pubmed'].append({
                    'id': str(int(row['id'])),
                    'title': row['title'],
                    'date': row['date']
                })

        # look into clinical_trials
        for _, row in in_df_clinical_trials.iterrows():
            if drug in row['title'].lower():
                journal_key = (row['journal'], row['date'])
                if journal_key not in journals_dict:
                    journals_dict[journal_key] = {
                        'title': row['journal'],
                        'date': row['date'],
                        'clinical_trial': [],
                        'pubmed': []
                    }
                journals_dict[journal_key]['clinical_trial'].append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'date': row['date']
                })
    
        # Add related journals to drugs
        for journal in journals_dict.values():
            drug_info['journals'].append(journal)

        # Add relations to results list
        results.append(drug_info)
    return results