import re
import unittest
from re import Pattern

from src.regex_catalog import RegexCatalog, UnknownRegexCatalogEntryError


class RegexCatalogTestCase(unittest.TestCase):

    def test_get_pattern(self) -> None:
        # given
        expected_pattern: Pattern = re.compile(RegexCatalog.ALPHANUMERIC_EXTENDED, flags=re.IGNORECASE)
        alphanumeric_extended_regex: str = RegexCatalog.ALPHANUMERIC_EXTENDED
        # when
        actual_pattern: Pattern = RegexCatalog.get_pattern(alphanumeric_extended_regex, flags=re.IGNORECASE)
        # then
        self.assertEqual(expected_pattern, actual_pattern)

    def test_get_pattern_not_in_catalog(self) -> None:
        # given
        not_in_catalog_regex_name: str = "ASCII_EXTENDED"
        # then
        with self.assertRaises(UnknownRegexCatalogEntryError) as e:
            RegexCatalog.get_pattern(not_in_catalog_regex_name)

        self.assertEqual("Regex not defined in PatternCatalog: {}".format(not_in_catalog_regex_name), str(e.exception))


if __name__ == '__main__':
    unittest.main()
