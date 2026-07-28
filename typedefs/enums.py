from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter import Widget

    from models import Sample

    from .base_types import SaveObject


class GraphType(Enum):
    """
    An Enum representing the graph types:
    - CUM -----> cumulative.
    - HIST ----> histogram.
    """
    HIST = 0
    CUM = 1


class LogMsgType(Enum):
    """
    An Enum representing various log massage types:
    - NORMAL -----> normal massage.
    - WARNING ----> warning massage.
    - ERROR ----> error massage.
    """
    NORMAL = ''
    WARNING = '<!> Warning: '
    ERROR = '<!> Error: '


@dataclass
class SignalSchema():
    """
    Use to define the signal schema.
    """
    name: str
    args: tuple


class Signal(Enum):
    """
    An Enum representing the signals, done to mitigate the string trap:\n
    Use print(Signal.name.value) to know the args to pass into the lister.
    - LOG: signal to log a massage into the [LoggingPanel] --> args=[str, LogMsgType].
    - ANALYZE: signals the [AnalysisPanel] to analyze the data --> args=[sample, graph_type].
    - EXPORTED: signals [FilePanel] the end of the exporting process --> args=[].
    - EXPAND: signals the [MainPanel] to expand a Widget --> args=[Widget].
    - COLOR: signals the [FilePanel] to update the [SaveObject] color --> args=[color].
    """
    LOG = SignalSchema('log', (str, LogMsgType))
    ANALYZE = SignalSchema('analyze', ('Sample', 'SaveObject', GraphType|None))
    EXPORTED = SignalSchema('exported', ())
    EXPAND = SignalSchema('expand', ('Widget',))
    COLOR = SignalSchema('color', (str,))

    def __lt__(self, other) -> bool:
        return len(self.value.args) < len(other)
    
    def __gt__(self, other) -> bool:
        return len(self.value.args) > len(other)

    def __repr__(self) -> str:
        return self.value.name

    def __str__(self) -> str:
        return self.value.name


class FileFormat(Enum):
    """
    An Enum representing the data file's formats:
    - EXCEL ----> .xlsx excel file.
    - CSV ------> .csv file.
    """
    EXCEL = 'xlsx'
    CSV = 'csv'


class AnalysisMethod(Enum):
    """
    An Enum representing the analysis method type:
    - TWO_POINTS ----> A special case where the sample only has less than three data points.
    - GRAPHICAL ----> graphical method using Folk&Ward, 1957 equations.
    - MOMENTS ------> the statistical moments based method.
    """
    TWO_POINTS = 'Two Points'
    GRAPHICAL = 'Graphical'
    MOMENTS = 'Method of Moments'


class SkewnessSchema(Enum):
    """
    An Enum representing the verbal interpretation schema.
    - ANASEDI -------> Analytical Sedimentology book.
    - FOLKWARD57 ----> Folk & Ward 1957 article.
    - OBSERVATIONAL -> A more intuitive version ANASEDI, basically, it's the same, but inverted.
    """
    ANASEDI = 0
    FOLKWARD57 = 1
    OBSERVATIONAL = 3