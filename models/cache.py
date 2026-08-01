from tkinter import Widget
from typing import Any, Sequence, TypeVar

from typedefs import SaveObject

Element = TypeVar('Element')

class Cache():
    """
    Caching functionality.
    """
    def __init__(self, size: int = 1000) -> None:
        """
        Caching functionality.
        - size: sets the size limit, in terms of number of entries
        """
        self.data: dict = {}
        self.limit = size

    def __repr__(self) -> str:
        return f'Data ID\'s: {self.data.keys()}\nSize: {self.size()}'

    def check(self, id_: str, against: Sequence[Any] = []) -> bool:
        """
        Checks if item with the [id] is cached then does a length/size comparison with [against] if provided, otherwise, it assumes that it's not needed.
        - against: a python sequence, e.g., list, tuple, etc, to compare against.
        """
        _valid_id: bool = id_ in self.data
        _valid_data: bool = len(self.data[id_]) == len(against) if _valid_id and against else True
        return _valid_id and _valid_data
    
    def size(self) -> int:
        """
        The overall cache size.
        """
        return len(self.data)

    def add(self, id_: str, widget) -> None:
        """
        Adds element using the given [id_] to the cache.
        """
        if id_ not in self.data:

            self.data[id_] = widget.copy() if isinstance(widget, SaveObject) else widget
        
        # Limit size:
        if self.size() > self.limit:
            _keys = [i for i in self.data.keys()][-self.limit:]
            self.data = self.data.fromkeys(_keys)
    
    def remove(self, id_: str) -> None:
        """
        Removes item at [id_] from the cache.
        """
        if id_ in self.data:
            _ = self.data.pop(id_)  

    def get(self, id_: str) -> Any:        
        """
        Gets the element at the given [id_] from the cache.
        - make sure the item is cached first!.
        - if the item isn't in the cache, return -> [].
        """
        _output = []
        if self.check(id_):
            _output = self.data[id_]
            _output = _output.copy() if isinstance(_output, SaveObject) else _output
        else:
            print(f'<!> Error:\n  > Item with id {id_} is not found in Cache, make sure to call .check first!')
            quit()
        return _output
    
    def see_all(self) -> None:
        return print(self.data)