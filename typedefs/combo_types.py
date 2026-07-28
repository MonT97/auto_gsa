from dataclasses import dataclass

from models import Analyzer

from .enums import GraphType


@dataclass
class GraphParameters():
    """
    Object housing parameters needed for graph creation.
    - graph_type: from the enum [GraphType].
    """
    analyzer: Analyzer = Analyzer()
    sample_name: str = ''
    graph_type: GraphType|None = GraphType.HIST
    graph_color: str = ''

    def __bool__(self) -> bool:
        return bool(self.sample_name)

    def keys(self):
        return self.__dict__.keys()
    
    def __getitem__(self, key: str):
        return getattr(self, key)

    def update(self, **kwargs) -> None:
        """
        Updates the instance values in-place.
        kwargs:
        - analyzer.: Analyzer
        - sample_name: str.
        - graph_type: GraphType.
        - graph_color: str.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError