import pandas as pd
import re
from collections import defaultdict
from itertools import chain
from functools import reduce


# Perform a forward filling followed by a backward filling to a GroupBy Object
def merge_rows(df_grouped):
    return df_grouped.ffill().bfill().iloc[0]


# Replace 'nan' strings with actual NaN values (useful for finding and filling missing values later)
def fix_nan(input_df: pd.DataFrame):
    for c in input_df.columns:
        input_df.loc[input_df[c] == 'nan', [c]] = None


# Rename old_col_name to title in order to have uniform column names in both dataframes (clinical_tirals and pubmed)
def rename_title(input_df: pd.DataFrame, old_col_name: str):
    input_df.rename(columns={old_col_name: "title"}, inplace=True)


# Filling missing journal values based on title (groupby title)
def fill_group_values(input_df: pd.DataFrame, group_col_name: str):
    df_filled = input_df.groupby(group_col_name, sort=False).apply(
        merge_rows).reset_index(drop=True)
    return df_filled


def drop_duplicates_df(input_df, subset):
    if subset:
        input_df.drop_duplicates(subset, inplace=True)
    else:
        input_df.drop_duplicates(inplace=True)


# Remove empty 'title' strings (len < 1)
def drop_records_with_empty_titles(input_df: pd.DataFrame):
    input_df.drop(input_df[input_df.title.map(len)
                           < 1].index, inplace=True)


# Remove leading and trailing whitespaces and convert all text to lowercase
def strip_and_lower_str(txt_: str):
    return txt_.strip().lower()


# Convert all dates to one uniform format (dd/mm/YYYY)
def uniform_dates(input_df: pd.DataFrame):
    input_df.date = input_df.date.apply(
        lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))


"""
remove_undecoded_chars handles (eliminates) undecoded characters like \xc3 and \x28 in the data (journal and title).
    Args:
    input_df: pd.DataFrame = data
    col_name: str = target column where the operation will run.
"""


def remove_undecoded_chars(input_df: pd.DataFrame, col_name: str):
    input_df[col_name] = input_df[col_name].apply(
        lambda x: re.sub('\\\\.\w{1,3}', '', x))


"""
clean_data performs the following actions:
    - Replacing 'nan' strings with actual null values
    - Renaming title column name to title in order to have the same column names in pubmed and clinical_trials data
    - Removing duplicates based on title for pubmed and clinical_trials and based on atccode for drugs
    - Removing empty strings in title (+trailing and leanding whitespaces)
    - Converting dates to one unique format (dd/mm/YYYY)

    Args:
    input_df: pandas.DataFrame
"""


def clean_data(input_df: pd.DataFrame):
    # Replace 'nan' strings with actual NaN values (useful for finding and filling missing values later)
    fix_nan(input_df)
    # Rename scientific_title to title in order to have the same column name in both dataframes (clinical_tirals and pubmed)
    if 'scientific_title' in input_df.columns:
        rename_title(input_df, 'scientific_title')
        # Filling missing journal values based on title (groupby title)
        input_df = fill_group_values(input_df, 'title')

    # Also remove duplicates based on title as the id can be null
    if 'title' in input_df.columns:
        drop_records_with_empty_titles(input_df)
        drop_duplicates_df(input_df, 'title')
        input_df.title = input_df.title.apply(strip_and_lower_str)
        input_df.journal = input_df.journal.apply(strip_and_lower_str)
        # Remove undecoded utf-8 chars using regex
        remove_undecoded_chars(input_df, 'title')
        remove_undecoded_chars(input_df, 'journal')
        # And finally convert all dates to one uniform format (dd/mm/YYYY)
        uniform_dates(input_df)

    # As for drugs data 'atccode' is the identifier and no anomalies have been observed so we can use it to remove duplicates
    else:
        drop_duplicates_df(input_df, 'atccode')
        input_df.drug = input_df.drug.apply(strip_and_lower_str)
    return input_df


# Return a 'cleaned' version of each input dataframe
def clean_project_data(clinical_trials_data: pd.DataFrame, pubmed_data: pd.DataFrame, drugs_data: pd.DataFrame):
    return clean_data(clinical_trials_data), clean_data(pubmed_data), clean_data(drugs_data)


"""
generate_graph creates a json graph to model relations between drugs and journals based on publications from
PubMed and clinical trials
    Args:
    in_df_clinical_trials: pd.DataFrame corresponds to clinical trials data
    in_df_pubmed: pd.DataFrame corresponds to PubMed data
    in_df_drugs: pd.DataFrame corresponds to drugs data

"""


def generate_graph(in_df_clinical_trials: pd.DataFrame, in_df_pubmed: pd.DataFrame, in_df_drugs: pd.DataFrame):

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
            if drug in row['title']:
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
            if drug in row['title']:
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

# ---------- BONUS - ad-hoc ----------
# PART I - Extract the journal that mentions the most different drugs


def extract_journal_with_most_drugs(data_):

    # Initialize a defaultdict of sets
    journal_to_drugs = defaultdict(set)

    # Flatten all journals and map them to drugs using chain()
    journal_entries = chain.from_iterable(
        [(journal['title'], item['drug']) for journal in item['journals']]
        for item in data_
    )

    # Fill journal_to_drugs using map
    list(map(lambda jd: journal_to_drugs[jd[0]].add(jd[1]), journal_entries))

    # Use reduce to find the max count of unique drugs across journals
    max_count = reduce(
        lambda acc, item: max(acc, len(item[1])),
        journal_to_drugs.items(),
        0
    )

    # Collect all journals with the max_count
    max_journals = [journal for journal,
                    drugs in journal_to_drugs.items() if len(drugs) == max_count]

    # Output the answer
    return (f"Journal(s) with the most unique drugs: '{max_journals}' linked to {max_count} unique drugs.")

# ---------- BONUS - ad-hoc ----------
# PART II - Find related drugs mentioned by the same journals, referenced by PubMed but not by clinical trials


def find_related_drugs_not_in_clinical_trials(target_drug, data_):
    related_drugs = set()
    unrelated_drugs = set()
    # Find journals that mentions the specified drug
    target_journals = set(
        journal['title']
        for item in data_ if item['drug'] == target_drug
        for journal in item['journals'] if 'clinical_trial' not in journal
    )
    # Find related drugs mentioned by the same journals, referenced by PubMed but not by clinical trials
    for item in data_:
        for journal in item['journals']:
            if journal['title'] in target_journals:
                if 'clinical_trial' in item['journals']:
                    unrelated_drugs.add(item['drug'])
                related_drugs.add(item['drug'])
    # Discard the target drug from related drugs list
    related_drugs.discard(target_drug)
    # Discard drugs mentioned in journals referenced by clinical trials
    related_drugs_ = [
        element for element in related_drugs if element not in unrelated_drugs]
    return related_drugs_
