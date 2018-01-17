__author__ = "MULTIPLY Team"


class AttributeDict(object):
    """
    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
    """
    def __init__(self, **entries):
        self.add_entries(**entries)

    def add_entries(self, **entries):
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(**value)
            else:
                self.__dict__[key] = value

    def has_entry(self, entry: str):
        return self._has_entry(entry, 0)

    def _has_entry(self, entry: str, current_index: int):
        entry_keys = entry.split('.')
        if entry_keys[current_index] in self.__dict__.keys():
            if current_index < len(entry_keys):
                dict_entry = self.__dict__[entry_keys[current_index]]
                if type(dict_entry) is not dict:
                    return False
                return dict_entry._has_entry(entry, current_index + 1)
            return True
        return False

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)
