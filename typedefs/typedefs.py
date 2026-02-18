from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np

type SamplePoints = list[tuple[float, float]]
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

@dataclass
class SampleStats():

    mean: float = 0.0
    std: float = 0.0
    kurtosis: float = 0.0
    skewness: float = 0.0
    
    def to_dict(self) -> dict[str, float]:
        return self.__dict__
    
@dataclass
class StatsInterpretation():
    
    sorting: str = ""
    skewness: str = ""
    kurtosis: str = ""

    def to_dict(self) -> dict[str, str]:
        return self.__dict__