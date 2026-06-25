import os

from collections.abc import Callable

import numpy as np
import pandas as pd

class Sample():
    """
    The class resembling the sample:
        - name: str.
        - data: pd.DataFrame, a minimum of 3 points is necessary for calculations.
    """
    samples_list: list = []
    def __init__(self, path: str = "") -> None:
        
        self._full_name, self._data = self._create_data(path)
        
    def __repr__(self) -> str:

        return f"{__class__.__name__} ({self._full_name=}, {self._data=})"
    
    def __eq__(self, other) -> bool:
        
        return True if (self._full_name == other._full_name) and (self._data.equals(other._data)) else False

    def _create_data(self, path: str) -> tuple[str, pd.DataFrame]:
        """
        Creates the data, returns:
            - name [str]: the sample name.
            - data [pd.DataFrame]: the data itself.
        """
        _full_name: str = ''
        _format: str = ''
        _data = pd.DataFrame()

        if path:
            _full_name: str = os.path.split(path)[-1]
            _format: str = _full_name.split('.')[-1]

            #centeralizes the read mothod scelection.
            _fmt_func_dict: dict[str, Callable] = {
                    'csv': pd.read_csv,
                    'xlsx': pd.read_excel
                    }
            _read_fn: Callable[[str], pd.DataFrame] = lambda fmt: _fmt_func_dict[fmt](path)
            
            #TODO make it column name agnositc using iloc[]!
            _data: pd.DataFrame = _read_fn(_format)
            _data.replace({'wht': {0.0: np.nan}}, inplace=True) #type: ignore

            _data['wht%'] = ((_data['wht']/_data['wht'].sum())*100).round(2)
            _data['cum.wht%'] = _data['wht%'].cumsum().round(2)
            Sample.samples_list.append(self)
        
        return (_full_name, _data)
    
    def get_name(self, full: bool = False) -> str:
        """
        full: returns [file_name.format] if true.
        """
        _short_name: str = self._full_name.split(".")[0].capitalize()

        return _short_name if not full else self._full_name      
    
    def get_data(self) -> pd.DataFrame:
        """
        Returns the sample data.
        """
        return self._data