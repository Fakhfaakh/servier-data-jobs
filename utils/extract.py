import pandas as pd
import os
import glob

"""
Extract data from csv files and return 3 dataframes each corresponding to one file
in data_path

data_path = string: Data location, any valid string path is acceptable.
"""


def load_data_from_csv(filename:str, data_path:str='./data'):
    df = pd.read_csv(os.path.join(f'{data_path}/', filename))
    return df


def extract_project_data(data_path_:str='./data', filenames:str=['clinical_trials', 'pubmed', 'drugs']):
    extension_ = 'csv'
    drugs_df, pubmed_df, clinical_trials_df = load_data_from_csv(f'{filenames[0]}.{extension_}', data_path_), load_data_from_csv(f'{filenames[1]}.{extension_}', data_path_), load_data_from_csv(f'{filenames[2]}.{extension_}', data_path_)
    return drugs_df, pubmed_df, clinical_trials_df