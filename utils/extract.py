import pandas as pd
import os
import glob


def load_data_from_csv(filename: str, data_path: str = './data'):
    """
    Extract data from csv files and a dataframe corresponding to a filename
    in data_path

    Args:
        filename: str = the file name of input data
        data_path: str = Data location, any valid string path is acceptable.
    returns:
        pd.DataFrame object
    """
    df = pd.read_csv(os.path.join(f'{data_path}/', filename))
    return df


def extract_project_data(data_path_: str = './data', filenames: str = ['clinical_trials', 'pubmed', 'drugs']):
    """
    Extract data from 3 csv files and return 3 dataframes each corresponding to a filename
    in data_path, filenames are optional, unless specified, it must be in the same order, drugs data, pubmed data, clinical trials data

    Args:
        filenames: list = 3 file names of input data
        data_path: str = Data location, any valid string path is acceptable.
    returns:
        3 pd.DataFrame object
    """
    extension_ = 'csv'
    drugs_df, pubmed_df, clinical_trials_df = load_data_from_csv(f'{filenames[0]}.{extension_}', data_path_), load_data_from_csv(
        f'{filenames[1]}.{extension_}', data_path_), load_data_from_csv(f'{filenames[2]}.{extension_}', data_path_)
    return drugs_df, pubmed_df, clinical_trials_df
