from dataclasses import dataclass

from .enums import GraphType
from models import Analyzer

@dataclass
class GraphParameters():
    """
    Object housing parameters needed for graph creation.
    - graph_type: from the enum [GraphType].
    """
    analyzer: Analyzer = Analyzer()
    sample_name: str = ''
    graph_type: GraphType = GraphType.HIST
    graph_color: str = ''

    def to_dict(self) -> dict:
        return self.__dict__