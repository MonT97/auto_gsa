from dataclasses import dataclass
from enum import Enum
from tkinter import Widget
from types import UnionType
from typing import Any

from models import Analyzer, Sample

from .base_types import SaveObject
from .enums import GraphType, LogMsgType


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


@dataclass
class SignalSchema():
    """
    Use to define the signal schema.
    """
    name: str
    args: tuple[Any,...]


class Signal(Enum):
    """
    An Enum representing the signals, done to mitigate the string trap:\n
    Use print(Signal.name.value) to know the args to pass into the lister.
    - LOG: signal to log a massage into the [LoggingPanel].
    - ANALYZE: signals the [AnalysisPanel] to analyze the data.
    - EXPORTED: signals [FilePanel] the end of the exporting process.
    - EXPAND: signals the [MainPanel] to expand a Widget.
    - COLOR: signals the [FilePanel] to update the [SaveObject] color.
    """
    LOG = SignalSchema('log', (str, LogMsgType|None))
    ANALYZE = SignalSchema('analyze', (Sample, SaveObject, GraphType|None))
    EXPORTED = SignalSchema('exported', ())
    EXPAND = SignalSchema('expand', (Widget,))
    COLOR = SignalSchema('color', (str,))

    def __lt__(self, other) -> bool:
        return len(self.value.args) < len(other)
    
    def __gt__(self, other) -> bool:
        return len(self.value.args) > len(other)

    def get_name(self) -> str:
        return self.value.name

    def get_args(self) -> tuple[Any,...]:
        """
        Returns the [args] from the SignalSchema.
        """
        return self.value.args