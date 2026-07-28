from typing import Any, Sequence, TypeVar

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
            self.data[id_] = widget
        
        # Limit size:
        if self.size() > self.limit:
            _keys = [i for i in self.data.keys()][-self.limit:]
            self.data = self.data.fromkeys(_keys)
    
    def get(self, id_: str) -> list:        
        """
        Gets the element at the given [id_] from the cache.
        - make sure the item is cached first!.
        - if the item isn't in the cache, return -> [].
        """
        if id_ not in self.data:
            _output = []
            print(f"Item{id_} isn't cached!!, call Cache.check({id_})!")
        else:
            _output = self.data[id_]
        return _output