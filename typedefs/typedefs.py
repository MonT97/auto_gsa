from enum import Enum

import pandas as pd
import numpy as np

type SamplePoints = list[tuple[float, float]]
type SampleStats = dict[str, float]
type PlotInput = pd.Series|np.ndarray
type PlotData = tuple[PlotInput, PlotInput, SamplePoints]


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