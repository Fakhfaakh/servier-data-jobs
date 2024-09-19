import argparse
from utils.load import load_data
from utils.extract import extract_data
from utils.transform import clean_data, generate_graph, extract_journal_with_most_drugs, find_related_drugs_not_in_clinical_trials
import logging

logger = logging.getLogger(__name__)

def generate_drugs_graph(data_path_:str, destination_:str):
    # loading data
    clinical_trials, pubmed, drugs = extract_data(data_path_)
    logger.info("------ DATA SUCCESSFULLY EXTRACTED")
    # cleaning data
    clinical_trials, pubmed, drugs = clean_data(clinical_trials), clean_data(pubmed), clean_data(drugs)
    logger.info("------ DATA SUCCESSFULLY CLEANED")

    # building the graph
    graph = generate_graph(clinical_trials, pubmed, drugs)
    logger.info("------ GRAPH SUCCESSFULLY GENERATED")

    # loading data into a json file
    load_data(graph, destination_)
    logger.info("------ DATA SUCCESSFULLY LOADED")
    return graph

if __name__ == "__main__":
    # setting the logging level to INFO
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    parser = argparse.ArgumentParser(description="Generate drugs JSON graph from publications issued from clinical trials and PubMed publications")
    parser.add_argument('--data_path', required=True, help='Path to the directory containing input CSV files.')
    parser.add_argument('--destination', required=True, help='Destination path for the output JSON file.')
    parser.add_argument('--bonus', action='store_true', help='Bonus-part--Journal that mentions the most different drugs')
    parser.add_argument('--target_drug', help='Bonus-part--Specify a drug to get related drugs mentioned by the same journals ref by PubMed but not by clinical trials')

    args = parser.parse_args()
    graph = generate_drugs_graph(args.data_path, args.destination)
    if args.bonus:
        logger.info(extract_journal_with_most_drugs(graph))
    if args.target_drug:
        logger.info(f'Related drugs are: {find_related_drugs_not_in_clinical_trials(args.target_drug, graph)}')