import unittest
import pandas as pd
from utils.transform import clean_data
from pandas.testing import assert_frame_equal


class TestTransform(unittest.TestCase):
    """
    This tests if data is cleaned properly, cases studied include:
        - "nan" string values
        - unformatted dates
        - duplicates with missing values in one row but exist in the other.
        - undecoded string chars like \x36
        - strings with trailing and leading whitespaces
    """
    input_ = {}
    expected_transformed_input_ = {}

    @classmethod
    def init_input(test_object):
        test_object.input_ = {
            "id": [
                "1",
                "2",
                "nan",
                "4",
                "5"
            ],
            "title": [
                r"title with \x36\xc8 decoding errors!",
                "Simulating Tetracycline          ",
                "Use of Diphenhydramine as an Adjunctive Sedative for Colonoscopy",
                "Use of Diphenhydramine as an Adjunctive Sedative for Colonoscopy",
                "An article"
            ],
            "date": [
                "01/02/2021",
                "2020-07-12",
                "1 April 2021",
                "01/04/2021",
                "24 January 2022"
            ],
            "journal": [
                "nan",
                r"  Psychopharmacology \x23",
                "  Hôpitaux Universitaires de (Génève)  ",
                " ",
                "Journal of emergency nursing"
            ]
        }
        test_object.expected_transformed_input_ = {
            "id": [
                "1",
                "2",
                "4",
                "5"
            ],
            "title": [
                "title with  decoding errors!",
                "simulating tetracycline",
                "use of diphenhydramine as an adjunctive sedative for colonoscopy",
                "an article"
            ],
            "date": [
                "02/01/2021",
                "12/07/2020",
                "01/04/2021",
                "24/01/2022"
            ],
            "journal": [
                "",
                "psychopharmacology ",
                "hôpitaux universitaires de (génève)",
                "journal of emergency nursing"
            ]
        }

    def test_clean(self):
        self.init_input()
        self.input_df = pd.DataFrame(
            self.input_, columns=["id", "title", "date", "journal"])
        self.expected_df = pd.DataFrame(self.expected_transformed_input_, columns=[
                                        "id", "title", "date", "journal"])
        assert_frame_equal(self.expected_df.reset_index(
            drop=True), clean_data(self.input_df).reset_index(drop=True))


if __name__ == "__main__":
    unittest.main()
