import unittest

from src.tokenizer import Tokenizer
from src.regex_catalog import RegexCatalog


class TokenizerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tokenizer = Tokenizer(regex=RegexCatalog.ALPHANUMERIC_EXTENDED, word_delimiter="#")

    def test_get_tokens(self) -> None:
        raw_string: str = "one-two#three"
        actual_tokens: set[str] = self._tokenizer.get_tokens(raw_string)
        self.assertSetEqual({"one-two", "three"}, actual_tokens)

    def test_get_tokens_split_unknown_regex_symbols(self) -> None:
        # get_tokens returns a set, so no duplicate tokens can be present
        raw_string: str = "one!two is not one-two nor one two"
        actual_tokens: set[str] = self._tokenizer.get_tokens(raw_string)
        self.assertSetEqual({"one", "two", "is", "not", "one-two", "nor"}, actual_tokens)

    def test_tokenize_word(self) -> None:
        # tokenize_words returns a list, so duplicate tokens can be present
        raw_string: str = "one two is not one-two nor one#two"
        actual_tokens: list[str] = self._tokenizer.tokenize_word(raw_string)
        self.assertListEqual(["one", "two", "is", "not", "one-two", "nor", "one", "two"], actual_tokens)


if __name__ == '__main__':
    unittest.main()
