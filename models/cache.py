class Cache():
    """
    Caching functionality.
    """
    def __init__(self) -> None:
        self.data: dict = {}

    def check(self, id_: str) -> bool:
        """
        Checks if item with the [id] is cached.
        """
        return id_ in self.data

    def size(self) -> int:
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
    
    def get(self, _id: str):        
        """
        Gets the widget using the given [_id] from the cache.
        - must chech if the item is cached first.
        """
        _output = False
        if _id not in self.data:
            print(f"Item{_id} isn't cached!!")
        else:
            _output = self.data[_id]
        return _output