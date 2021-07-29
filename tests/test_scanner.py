import unittest
from src.scanner import Scanner


class ScannerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._scanner = Scanner(exit_word=":q",
                               prompt="search> ")

    # really dummy test...
    def test_is_exit_statement(self) -> None:
        self.assertTrue(self._scanner.is_exit_statement(self._scanner.exit_word))

    def test_is_exit_statement_false(self) -> None:
        # given
        not_exit_statement: str = self._scanner.exit_word + "dummy"
        # then
        self.assertFalse(self._scanner.is_exit_statement(not_exit_statement))


if __name__ == '__main__':
    unittest.main()
