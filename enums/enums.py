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