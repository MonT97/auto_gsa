from enum import Enum

class GraphType(Enum):
    """
    An Enum representing the graph types:
    - CUM -----> cumulative.
    - HIST ----> histogram.
    """
    HIST = 0
    CUM = 1


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
    - TWOPOINTS ----> A special case where the sample only has less than three data points.
    - GRAPHICAL ----> graphical method using Folk&Ward, 1957 equations.
    - MOMENTS ------> the statistical moments based method.
    """
    TWOPOINTS = 'Two Points'
    GRAPHICAL = 'Graphical'
    MOMENTS = 'Method of Moments'


class SkewnessSchema(Enum):
    """
    An Enum representing the verbal interpertation schema.
    - ANASEDI -------> Analytical Sedimentology book.
    - FOLKWARD57 ----> Folk & Ward 1957 article.
    - OBSERVATIONAL -> A more intuitive version ANASEDI, basically, it's the same, but inverted.
    """
    ANASEDI = 0
    FOLKWARD57 = 1
    OBSERVATION = 3