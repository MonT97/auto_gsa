from dataclasses import dataclass
from enum import Enum
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Any, get_args

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