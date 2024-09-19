import pandas as pd
import os
"""
Extract data from csv files and return 3 dataframes each corresponding to one file
in data_path

data_path = string: Data location, any valid string path is acceptable.
"""
def extract_data(data_path='./data/'):
    return pd.read_csv(os.path.join(data_path,'clinical_trials.csv')), pd.read_csv(os.path.join(data_path, 'pubmed.csv')), pd.read_csv(os.path.join(data_path,'drugs.csv'))