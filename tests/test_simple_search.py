import os.path
import unittest

import pandas as pd

from src.regex_catalog import RegexCatalog
from src.simple_search import SimpleSearch
from src.tokenizer import Tokenizer


class SimpleSearchTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._tokenizer = Tokenizer(regex=RegexCatalog.ALPHANUMERIC_EXTENDED, word_delimiter=" ")
        cls._simple_search = SimpleSearch(path=os.path.join(os.getcwd(), "tests", "samples"),
                                          valid_extensions=['txt'],
                                          tokenizer=cls._tokenizer)
        with open(os.path.join(os.getcwd(), "tests", "samples", "python_dict_queen"), "r") as f:
            cls._simple_search_dictionary = eval(f.read())

    def test_load_directory_into_database(self) -> None:
        # given
        file_count: int = 2
        # when
        self._simple_search.load_directory_into_database()
        # then
        self.assertEqual(file_count, len(self._simple_search.database_files))
        self.assertDictEqual(self._simple_search_dictionary, self._simple_search.database.dictionary)
        self._simple_search.clear_database()

    def test_load_directory_into_database_non_existing_path(self) -> None:
        # given
        non_existing_path: str = "does/not/exist"
        fail_simple_search: SimpleSearch = SimpleSearch(path=non_existing_path,
                                                        valid_extensions=["txt"],
                                                        tokenizer=self._tokenizer)
        # when-then
        with self.assertRaises(FileNotFoundError) as e:
            fail_simple_search.load_directory_into_database()
        self.assertEqual(0, len(fail_simple_search.database.dictionary))

    def test_get_file_extension(self) -> None:
        print(len(self._simple_search.database.dictionary))
        self.assertEqual("csv", SimpleSearch.get_file_extension("files/file.txt.csv"))
        self.assertEqual("txt", SimpleSearch.get_file_extension("file.txt"))
        self.assertIsNone(SimpleSearch.get_file_extension("file"))

    def test_get_search_hits_as_dataframe(self) -> None:
        # given
        query_tokens: set[str] = {"like", "bicycle", "just", "show"}
        expected_df_dict: dict[str, dict[str, int]] = {
            'like':     {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'show':     {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 0},
            'bicycle':  {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'just':     {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 1}
        }
        # when
        self._simple_search.load_directory_into_database()
        actual_df: pd.DataFrame = self._simple_search.get_search_hits_as_dataframe(query_tokens)

        # then
        self.assertDictEqual(expected_df_dict, actual_df.to_dict())
        self._simple_search.clear_database()

    def test_get_search_hits_as_dataframe_empty_query_tokens(self) -> None:
        # given
        empty_query_tokens: set[str] = {}
        expected_df_dict: dict[str, dict[str, int]] = {}
        # when
        self._simple_search.load_directory_into_database()
        actual_df: pd.DataFrame = self._simple_search.get_search_hits_as_dataframe(empty_query_tokens)

        # then
        self.assertDictEqual(expected_df_dict, actual_df.to_dict())
        self._simple_search.clear_database()

    def test_get_search_hits_as_dataframe_missing_query_tokens(self) -> None:
        # given
        empty_query_tokens: set[str] = {"this-token-does-not-exist", "neither-does-this-one"}
        expected_df_dict: dict[str, dict[str, int]] = {
            'neither-does-this-one':        {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 0},
            'this-token-does-not-exist':    {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 0}
        }
        # when
        self._simple_search.load_directory_into_database()
        actual_df: pd.DataFrame = self._simple_search.get_search_hits_as_dataframe(empty_query_tokens)

        # then
        self.assertDictEqual(expected_df_dict, actual_df.to_dict())
        self._simple_search.clear_database()

    def test_rank_dataframe_search_hits(self) -> None:
        # given
        df_dict_data: dict[str, dict[str, int]] = {
            'like':     {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'show':     {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 0},
            'bicycle':  {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'just':     {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 1}
        }
        expected_df_dict: dict[str, float] = {
            'queen_bicycle.txt': 50.0,
            'queen_bohemian_rhapsody.txt': 25.0
        }
        expected_df: pd.DataFrame = pd.DataFrame().from_dict(df_dict_data)

        # when
        actual_df: pd.DataFrame = self._simple_search.rank_dataframe_search_hits(expected_df)

        # then
        self.assertDictEqual(expected_df_dict, actual_df.to_dict())

    def test_rank_dataframe_search_hits_caps_top_n(self) -> None:
        # given
        df_dict_data: dict[str, dict[str, int]] = {
            'like': {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'show': {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 0},
            'bicycle': {'queen_bicycle.txt': 1, 'queen_bohemian_rhapsody.txt': 0},
            'just': {'queen_bicycle.txt': 0, 'queen_bohemian_rhapsody.txt': 1}
        }
        expected_df_dict: dict[str, float] = {
            'queen_bicycle.txt': 50.0
        }

        # when
        original_rank_result_limit: int = self._simple_search.RANK_RESULT_LIMIT
        simulated_df: pd.DataFrame = pd.DataFrame.from_dict(df_dict_data)
        actual_df: pd.DataFrame = SimpleSearch.rank_dataframe_search_hits(simulated_df, 1)

        # then
        self.assertDictEqual(expected_df_dict, actual_df.to_dict())


if __name__ == '__main__':
    unittest.main()
