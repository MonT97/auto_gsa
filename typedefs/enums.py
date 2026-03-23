from enum import Enum

class GraphType(Enum):
    '''
    An Enum representing the graph types:
    - CUM -----> cumulative.
    - HIST ----> histogram.
    '''
    HIST = 0
    CUM = 1


class FileFormat(Enum):
    '''
    An Enum representing the data file's formats:
    - EXCEL ----> .xlsx excel file.
    - CSV ------> .csv file.
    '''
    EXCEL = 'xlsx'
    CSV = 'csv'


class AnalysisMethod(Enum):
    '''
    An Enum representing the analysis method type:
    - GRAPHICAL ----> Folk&Ward graphical method.
    - MOMENTS ------> the statistical moments based method.
    '''
    GRAPHICAL = 'Graphical'
    MOMENTS = 'Method of Moments'