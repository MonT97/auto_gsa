from dataclasses import dataclass

import pandas as pd
import numpy as np

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
    
@dataclass
class StatsInterpretation():
    
    sorting: str = ""
    skewness: str = ""
    kurtosis: str = ""

    def to_dict(self) -> dict[str, str]:
        return self.__dict__