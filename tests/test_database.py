import unittest
from src.database import Database, DictionaryKey, DictionaryValue, SetDictionaryValue


class DatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._database = Database()

    def test_add(self) -> None:
        # given
        self._database.dictionary.clear()
        # when
        self._database.add(DictionaryKey('key1'), DictionaryValue("one"))
        self._database.add(DictionaryKey('key1'), DictionaryValue("two"))
        # then
        self.assertEqual(1, len(self._database.dictionary))

    def test_add_empty_key(self) -> None:
        # given
        self._database.dictionary.clear()
        # when-then
        with self.assertRaises(ValueError) as e:
            self._database.add(DictionaryKey(''), DictionaryValue("one"))

        self.assertEqual("Expected key and val to be provided.", str(e.exception))

    def test_add_empty_val(self) -> None:
        # given
        self._database.dictionary.clear()
        # when-then
        with self.assertRaises(ValueError) as e:
            self._database.add(DictionaryKey('key1'), DictionaryValue(''))

        self.assertEqual("Expected key and val to be provided.", str(e.exception))

    def test_add_repeated_value(self) -> None:
        # given
        self._database.dictionary.clear()
        key1: DictionaryKey = DictionaryKey('key1')
        val1: DictionaryValue = "one"
        expected_value: SetDictionaryValue = {"one"}
        # when
        self._database.add(key1, val1)
        self._database.add(key1, val1)
        actual_value: SetDictionaryValue = self._database.find(key1)
        # then
        self.assertSetEqual(expected_value, actual_value)

    def test_find(self) -> None:
        # given
        self._database.dictionary.clear()
        key1: DictionaryKey = DictionaryKey('key1')
        val1: DictionaryValue = "one"
        expected_value: SetDictionaryValue = {"one"}
        # when
        self._database.add(key1, val1)
        actual_value: SetDictionaryValue = self._database.find(key1)
        # then
        self.assertSetEqual(expected_value, actual_value)

    def test_find_missing(self) -> None:
        # given
        self._database.dictionary.clear()
        key1: DictionaryKey = DictionaryKey('key1')
        val1: DictionaryValue = "one"
        missing_key: DictionaryKey = DictionaryKey('key2')
        # when
        self._database.add(key1, val1)
        actual_value: SetDictionaryValue = self._database.find(missing_key)
        # then
        self.assertIsNone(actual_value)


if __name__ == '__main__':
    unittest.main()
