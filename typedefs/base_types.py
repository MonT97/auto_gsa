import os
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
    Data model for data needed for exporting/saving output data.\n
    Designed to wander around carrying data.
    - prefix: To append to the beginning of the file's name.
    - files_path: The dir housing the files.
    - results_path: To save the file within.
    - results_dir_name: The dir name.
    - raw_results_dir_name: Then name of dir to save raw files into.
    - color: The color of graph elements.
    - dpi: The png image resolution.
    - save_raw_files: If true a non interpreted spreadsheet would be exported as well.
    - interval: To inclusively export files between.
    - transparent: Sets the graph background to transparent.
    """
    prefix: str = ''
    files_path: str = ''
    results_path: str = ''
    results_dir_name: str = ''
    raw_results_dir_name: str = ''
    color: str = '' #!config
    dpi: int = 0
    save_raw_files: bool = False
    interval: tuple[int,list[int|None]] = (0,[])
    transparent: bool = False

    def get_results_path(self) -> str:
        """
        Returns the full path to the results dir.\n
        - -> os.path.join(results_path, results_folder_name)
        """
        return os.path.join(self.results_path, self.results_dir_name)