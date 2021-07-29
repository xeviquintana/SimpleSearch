import re
from enum import Enum, unique
from re import Pattern


class UnknownRegexCatalogEntryError(Exception):
    def __init__(self, regex) -> None:
        self.message = "Regex not defined in PatternCatalog: {}".format(regex)
        super().__init__(self.message)


@unique
class RegexCatalog(str, Enum):
    ALPHANUMERIC_EXTENDED: str = r"[a-zA-Z0-9_-]+"
    # can be extended by adding more entries that Tokenizer feels comfortable processing
    # ASCII: str = r"[^\x00-\x7F]+"

    @classmethod
    def get_pattern(cls, regex: str, flags=None) -> Pattern:
        if not RegexCatalog.has_value(regex):
            raise UnknownRegexCatalogEntryError(regex)

        try:
            return re.compile(regex, flags)
        except Exception as e:
            print("Could not compile regex: {}, flags: {}".format(regex, flags))
            raise e

    @classmethod
    def has_value(cls, regex: str) -> bool:
        return regex in cls._value2member_map_
