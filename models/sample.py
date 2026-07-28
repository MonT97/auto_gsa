import os
import re

import numpy as np
import pandas as pd

from utils.utls import import_form_path

# Constants
# df header:
HEADER: tuple = ('phi', 'wht', 'wht%', 'cum.wht%')

class Sample():
    """
    The class resembling the sample:
        - name: str.
        - data: pd.DataFrame, a minimum of 3 points is necessary for calculations.
    """
    def __init__(self, path: str = "") -> None:
        self._full_name: str = ''
        self._data: pd.DataFrame = pd.DataFrame()

        if path:
            self._full_name, self._data = self._create_data(path)
        
    def __repr__(self) -> str:

        return f"{__class__.__name__} ({self._full_name=}, {self._data.shape=})"
    
    def __eq__(self, other) -> bool:
        
        return True if (self._full_name == other._full_name) and (self._data.equals(other._data)) else False
    
    def _create_data(self, path: str) -> tuple[str, pd.DataFrame]:
        """
        Creates the data, returns:
            - full_name [str]: sample_name.ext.
            - data [pd.DataFrame]: the data itself.
        """
        _full_name: str = os.path.split(path)[-1]
        _format: str = _full_name.split('.')[-1]
        _data: pd.DataFrame = import_form_path(path, _format)
        
        #TODO: Some popup error crash??
        # We only assume 2*n col df.
        if min(_data.shape) > 2:
            return ('', pd.DataFrame())
        
        if _data.shape[1] > 2:
            _data = _data.T
        
        _fst_row: pd.Series = _data.iloc[0,:]
        _num_fst_row: bool = _fst_row.apply(lambda x: bool(re.match(r'[a-z]', f'{x}'))).sum() != 2
        _fst_row_no_match: bool = not _fst_row.equals(pd.Series(HEADER[:2]))
        _nw_header = HEADER[:2] if _fst_row_no_match else _fst_row
        
        if not _num_fst_row:
            _data = _data.iloc[1:,:].reset_index(drop=True).astype(np.float64)

        _crnt_header: np.ndarray = _data.columns.values
        _data.rename(columns={k: v for k,v in zip(_crnt_header, _nw_header)}, inplace=True)
        _data.replace({HEADER[1]: {0.0: np.nan}}, inplace=True)

        _data[HEADER[2]] = ((_data[HEADER[1]]/_data[HEADER[1]].sum())*100).round(2)
        _data[HEADER[3]] = _data[HEADER[2]].cumsum().round(2)
        
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