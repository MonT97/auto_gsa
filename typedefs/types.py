from dataclasses import dataclass

import numpy as np
import pandas as pd

type SamplePoints = list[tuple[float, float]]
type PlotInput = pd.Series|np.ndarray
type PlotData = tuple[PlotInput, PlotInput, SamplePoints]


@dataclass
class SampleStats():

    mean: float = 0.0
    std: float = 0.0
    kurtosis: float = 0.0
    skewness: float = 0.0
    
    def to_dict(self) -> dict[str, float]:
        return self.__dict__
    
    def to_frame(self) -> pd.DataFrame:
        _frame = pd.DataFrame(
            {'statistic': list(self.__dict__.keys()), 'values': list(self.__dict__.values())}
            )
        return _frame
    
@dataclass
class StatsInterpretation():
    
    sorting: str = ""
    kurtosis: str = ""
    skewness: str = ""

    def to_dict(self) -> dict[str, str]:
        return self.__dict__
    
    def to_frame(self) -> pd.DataFrame:
        _frame = pd.DataFrame(
            {'statistic': list(self.__dict__.keys()),
             'interpretation': list(self.__dict__.values())}
            )
        return _frame