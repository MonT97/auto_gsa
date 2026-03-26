from dataclasses import dataclass
from .enums import *

import numpy as np
import pandas as pd

type PlotData = tuple[PlotInput, PlotInput, SamplePoints, AnalysisMethod]
type SamplePoints = list[tuple[float, float]]
type PlotInput = pd.Series|np.ndarray


@dataclass
class SampleStats():
    '''
    An object holding the calculated sample statistics.
    '''
    mean: float = 0.0
    std: float = 0.0
    kurtosis: float = 0.0
    skewness: float = 0.0
    
    def to_dict(self) -> dict[str, float]:
        return self.__dict__
    
    def to_frame(self) -> pd.DataFrame:
        _frame = pd.DataFrame(
            {'statistic': list(self.__dict__.keys()),
             'values': list(self.__dict__.values())}
            )
        return _frame
    
@dataclass
class StatsInterpretation():
    '''
    An object holding the interpretation of the calculated sample stats.
    '''
    sorting: str = ''
    kurtosis: str = ''
    skewness: str = ''

    def to_dict(self) -> dict[str, str]:
        return self.__dict__
    
    def to_frame(self) -> pd.DataFrame:
        _frame = pd.DataFrame(
            {'statistic': list(self.__dict__.keys()),
             'interpretation': list(self.__dict__.values())}
            )
        return _frame

#change into pass around object, no not the best case!
@dataclass
class SaveObject():
    '''
    Under development.
    '''
    prefix: str = ''
    resutls_path: str = ''
    results_folder_name: str = ''
    color: str = '#1f7bb4' #!config
    interval = tuple()
    
    def to_dict(self) -> dict:
        return self.__dict__
    