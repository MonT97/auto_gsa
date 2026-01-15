from enum import Enum

class GraphType(Enum):
    '''
        Enum representing graph types:
        - CUM ---> cumulative.
        - HIST ---> histogram.
    '''
    CUM = 0
    HIST = 1