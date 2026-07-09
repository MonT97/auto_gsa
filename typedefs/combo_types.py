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

    def to_dict(self) -> dict:
        return self.__dict__