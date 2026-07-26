from dataclasses import dataclass
from typing import Any

import customtkinter as ctk
import numpy as np
import pandas as pd

from .enums import *

type ImportCacheElement = tuple[str, ctk.CTkFrame, ctk.CTkCheckBox, ctk.CTkLabel, ctk.CTkLabel]
type PlotData = tuple[PlotInput, PlotInput, SamplePoints, AnalysisMethod]
type SamplePoints = list[tuple[float, float]]
type PlotInput = pd.Series[Any]|np.ndarray[Any, Any]

@dataclass
class SampleStats():
    """
    An object holding the calculated sample statistics.
    """
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
    """
    An object holding the interpretation of the calculated sample stats.
    """
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

#! is This really needed??
@dataclass
class DefaultObj():
    """
    A base class, intended to be used as a base class for all [DefaultObj]s.
    """
    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class SaveObject(DefaultObj):
    """
    Data model for data needed for exporting/saving output data.
    - prefix: To append to the beginning of the file's name.
    - results_path: To save the file within.
    - results_folder_name: The dir name.
    - color: The color of graph elements.
    - dpi: The png image resolution.
    - save_raw_files: If True a non interpreted spreadsheet would be exported as well.
    - interval: To inclusively export files between.
    """
    prefix: str = ''
    results_path: str = ''
    results_folder_name: str = ''
    color: str = '' #!config
    dpi: int = 0
    save_raw_files: bool = False
    interval: tuple = ()
    transparent: bool = False