DictionaryKey = str
DictionaryValue = str
SetDictionaryValue = set[str]
SetDictionary = dict[DictionaryKey, SetDictionaryValue]


class Database:
    _dictionary: SetDictionary = None
    
    def __init__(self) -> None:
        self._dictionary = {}
    
    @property
    def dictionary(self) -> SetDictionary:
        return self._dictionary

    def add(self, key: DictionaryKey, val: DictionaryValue) -> None:
        if not key or not val:
            raise ValueError("Expected key and val to be provided.")
        
        if key not in self._dictionary:
            self._dictionary[key] = SetDictionaryValue((val,))
        else:
            self._dictionary[key].add(val)
    
    def find(self, key: str) -> SetDictionaryValue or None:
        if key not in self.dictionary:
            return None
        
        return self.dictionary[key]
