import re
from .regex_catalog import RegexCatalog


class Tokenizer:
    def __init__(self, regex: str, word_delimiter: str) -> None:
        self._regex = regex
        self._word_delimiter = word_delimiter

    @property
    def regex(self) -> str:
        return self._regex

    @property
    def word_delimiter(self) -> str:
        return self._word_delimiter

    def get_tokens(self, raw_string: str) -> set[str]:
        tokens: set[str] = set()
        for word in raw_string.split(self.word_delimiter):
            [tokens.add(token.lower()) for token in self.tokenize_word(word) if token]

        return tokens

    def tokenize_word(self, word: str) -> [str]:
        match: list[str] = RegexCatalog.get_pattern(self.regex, flags=re.IGNORECASE).findall(word)
        if not match:
            return []
        return match
