class Cache():
    """
    Caching functionality.
    """
    def __init__(self, size: int = 1000) -> None:
        """
        - size: sets the size limit, in terms of number of entries
        """
        self.data: dict = {}
        self.size = size

    def check(self, id_: str) -> bool:
        """
        Checks if item with the [id] is cached.
        """
        return id_ in self.data

    def _get_size(self) -> int:
        """
        The length of the cache.
        """
        return len(self.data)

    def add(self, _id: str, widget) -> None:
        """
        Adds widget using the given [_id] to the cache.
        """
        if _id not in self.data:
            self.data[_id] = widget
        
        # Limit size:
        if self._get_size() > self.size:
            _keys = [i for i in self.data.keys()][-self.size:]
            self.data = self.data.fromkeys(_keys)
    
    def get(self, _id: str):        
        """
        Gets the widget using the given [_id] from the cache.
        - must chech if the item is cached first.
        """
        _output = False
        if _id not in self.data:
            print(f"Item{_id} isn't cached!!, call check!")
        else:
            _output = self.data[_id]
        return _output