from utils.utls import import_form_path

import pandas as pd
import numpy as np
import re
import os

# df header:
SAMPLE_HEADER: tuple = ('phi', 'wht', 'wht%', 'cum.wht%')

class Sample():
    """
    The class resembling the sample:
        - name: str.
        - data: pd.DataFrame, a minimum of 3 points is necessary for calculations.
    """
    def __init__(self, path: str = "") -> None:
        self.full_name: str = ''
        self.data: pd.DataFrame = pd.DataFrame()

        if path:
            self.full_name, self.data = self._create_data(path)
        
    def __repr__(self) -> str:

        return f"{__class__.__name__} ({self.full_name=}, {self.data=})"
    
    def __eq__(self, other) -> bool:
        
        return True if (self.full_name == other.full_name) and (self.data.equals(other.data)) else False
    
    def _create_data(self, path: str) -> tuple[str, pd.DataFrame]:
        """
        Creates the data, returns:
            - full_name [str]: sample_name.ext.
            - data [pd.DataFrame]: the data itself.
        """
        _full_name: str = os.path.split(path)[-1]
        _format: str = _full_name.split('.')[-1]
        _data: pd.DataFrame = pd.DataFrame()

        #TODO: centeralizes the read mothod scelection into another module maybe!?                
        _data = import_form_path(path, _format)
        
        # We only assume 2*n col df.
        #TODO: Some popup error crash??
        if min(_data.shape) > 2:
            return ('', pd.DataFrame())
        
        if _data.shape[1] > 2:
            _data = _data.T
        
        _fst_row: pd.Series = _data.iloc[0,:]
        _num_fst_row: bool = _fst_row.apply(lambda x: bool(re.match(r'[a-z]', f'{x}'))).sum() != 2
        _fst_row_no_match: bool = not _fst_row.equals(pd.Series(SAMPLE_HEADER[:2]))
        _nw_header = SAMPLE_HEADER[:2] if _fst_row_no_match else _fst_row
        
        if not _num_fst_row:
            _data = _data.iloc[1:,:].reset_index(drop=True).astype(np.float64)

        _crnt_header: np.ndarray = _data.columns.values
        _data.rename(columns={k: v for k,v in zip(_crnt_header, _nw_header)}, inplace=True)
        _data.replace({SAMPLE_HEADER[1]: {0.0: np.nan}}, inplace=True)

        _data[SAMPLE_HEADER[2]] = (
                    (_data[SAMPLE_HEADER[1]]/_data[SAMPLE_HEADER[1]].sum())*100).round(2)
        _data[SAMPLE_HEADER[3]] = _data[SAMPLE_HEADER[2]].cumsum().round(2)
        
        return (_full_name, _data)
    
    def get_name(self, full: bool = False) -> str:
        """
        full: returns [file_name.format] if true.
        """
        _short_name: str = self.full_name.split(".")[0].capitalize()

        return _short_name if not full else self.full_name      
    
    def get_data(self) -> pd.DataFrame:
        """
        Returns the sample data.
        """
        return self.data