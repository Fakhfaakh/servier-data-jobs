import json


def load_data(data_: list, destination: str):
    """
    Saves data into a JSON file stored in data_path

    data_: list = a list of lists defining relations between drugs and journals
    destination: str = Destination path, where the final result will be loaded

    """
    with open(f'{destination}/drugs_graph_v1.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_, json_file, ensure_ascii=False, indent=2)
