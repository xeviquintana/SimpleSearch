import os
import pandas as pd

from argparse import ArgumentParser, Namespace
from collections import defaultdict
from database import Database, SetDictionary
from regex_catalog import RegexCatalog
from scanner import Scanner
from tokenizer import Tokenizer


class SimpleSearch:
    RANK_RESULT_LIMIT: int = 10

    def __init__(self, path: str, valid_extensions: [str], tokenizer: Tokenizer) -> None:
        self._path = path
        self._database = Database()
        self._database_files = list()
        self._valid_extensions = set(valid_extensions)
        self._tokenizer = tokenizer

    @property
    def path(self) -> str:
        return self._path

    @property
    def database(self) -> Database:
        return self._database

    @property
    def database_files(self) -> list[str]:
        return self._database_files

    @property
    def valid_extensions(self) -> [str]:
        return self._valid_extensions

    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    @staticmethod
    def parse_args() -> Namespace:
        parser = ArgumentParser(description="Index a directory, perform lookups on its file contents and rank results.")
        parser.add_argument("--path", help="Directory to scan to look for text files", type=str, required=True)

        return parser.parse_args()

    def clear_database(self) -> None:
        self._database = Database()
        self._database_files = list()

    def load_directory_into_database(self) -> None:
        try:
            files_in_dir: list[str] = os.listdir(self.path)
        except FileNotFoundError as e:
            raise e

        print("{} files in directory {}".format(len(files_in_dir), self.path))

        for filename in files_in_dir:
            self.dump_file_to_database(filename)

    def dump_file_to_database(self, filename: str) -> None:
        if not self.get_file_extension(filename) in self.valid_extensions:
            print("ignoring file {}: not a valid extension".format(filename))
            return

        self.database_files.append(filename)
        file_path: str = os.path.join(self.path, filename)
        with open(file_path, mode="r") as f:
            for line in f:
                self.fill_database(filename, line)

    @staticmethod
    def get_file_extension(filename: str) -> str or None:
        extension: str = filename.split(".")[-1]
        if filename == extension:
            return None
        return extension

    def fill_database(self, absolute_path: str, line: str) -> None:
        for token in self.tokenizer.get_tokens(raw_string=line):
            self._database.add(token, absolute_path)

    def interact(self, search_scanner: Scanner) -> None:
        query_string: str = search_scanner.read_input_as_string()
        while not search_scanner.is_exit_statement(query_string):
            tokens: set[str] = self.get_query_tokens(query_string)
            hits_df: pd.DataFrame = self.get_search_hits_as_dataframe(tokens)
            self.report_results(
                self.rank_dataframe_search_hits(hits_df))
            query_string = search_scanner.read_input_as_string()

    def get_query_tokens(self, query_string: str) -> set[str]:
        if not self.tokenizer:
            raise ValueError("Tokenizer must be set to get tokens from query.")

        return self.tokenizer.get_tokens(query_string)

    def get_search_hits_as_dataframe(self, query_tokens: set[str]) -> 'pd.DataFrame':
        """
        Build a dict that can be converted to a DataFrame. It relies on the order of files returned when calling
        self.database_files, that's why it's important it is a list() and not a set().
        Example. Having:
            self.database_files = ['f1.txt', 'f2.txt', 'f3.txt'],
            'token1' being inside f1.txt,
            'token2' being in f2.txt,
            'token3' being in the three of them, shape of df_dict will be:
        df_dict = {
            'token1': [1, 0, 0],
            'token2': [0, 1, 0],
            'token3': [1, 1, 1]
        }
        And the returning DataFrame will have as index the files in self.database_files, columns will be tokens and
         rows will be hits for the given file and token:
                  token1, token2, token3
        f1.txt         1       0       1
        f2.txt         0       1       1
        f3.txt         0       0       1

        Cost of this function in time is: O(n_tokens * n_files)
        """
        df_dict: [str, list[str]] = defaultdict(list)
        for token in query_tokens:
            matching_files: SetDictionary = self.database.find(token)
            if not matching_files:
                df_dict[token] = len(self.database_files) * [0]
            else:
                for file in self.database_files:
                    df_dict[token].append(int(file in matching_files))

        return pd.DataFrame(df_dict, index=self.database_files, columns=df_dict.keys())

    @staticmethod
    def rank_dataframe_search_hits(df: 'pd.DataFrame', top_n_rows: int = RANK_RESULT_LIMIT) -> 'pd.DataFrame':
        df = df[(df.T != 0).any()].copy()  # filtering files that didn't make any hit
        df['rank'] = round(df.sum(axis=1) / len(df.columns) * 100)  # simple rank function: hits(file) / #n_words
        df.sort_values(by=['rank'], ascending=False, inplace=True)

        return df['rank'].head(top_n_rows)

    @staticmethod
    def report_results(df: 'pd.Dataframe') -> None:
        if df.empty:
            print("no matches found")
            return

        for file in df.index:
            print("{}: {}%".format(file, int(df.at[file])))


if __name__ == "__main__":
    args: Namespace = SimpleSearch.parse_args()
    t: Tokenizer = Tokenizer(regex=RegexCatalog.ALPHANUMERIC_EXTENDED, word_delimiter=" ")

    simple_search: SimpleSearch = SimpleSearch(path=args.path, valid_extensions=['txt'], tokenizer=t)
    simple_search.load_directory_into_database()

    scanner: Scanner = Scanner(exit_word=":quit", prompt="search> ")
    simple_search.interact(scanner)
