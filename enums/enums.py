from enum import Enum

class GraphType(Enum):
    '''
        Enum representing graph types:
        - CUM -----> cumulative.
        - HIST ----> histogram.
    '''
    HIST = 0
    CUM = 1


class FileFormat(Enum):
    '''
        Enum representing data file's formats:
        - EXCEL ----> .xlsx excel file.
        - CSV ------> .csv file.
    '''
    EXCEL = 'xlsx'
    CSV = 'csv'