import os

from collections.abc import Callable

import pandas as pd

class Sample():
    '''
    The class resembling the sample:
        - name: str.
        - data: pd.DataFrame.
    '''
    samples_list: list = []
    def __init__(self, path: str = "") -> None:
        
        self._name, self._data = self._create_data(path)
        
    def __repr__(self) -> str:

        return f"{__class__.__name__} ({self._name=}, {self._data=})"
    
    def __eq__(self, other) -> bool:
        
        return True if (self._name == other._name) and (self._data.equals(other._data)) else False

    def _create_data(self, path: str) -> tuple[str, pd.DataFrame]:
        '''
        Creates the data, returns:
            - name [str]: the sample name.
            - data [pd.DataFrame]: the data itself.
        '''
        _name: str = ''
        _data = pd.DataFrame()

        if path:
            _name, _format = os.path.split(path)[-1].split('.')

            #centeralizes the read mothod scelection.
            _fmt_func_dict: dict[str, Callable] = {
                    'csv': pd.read_csv,
                    'xlsx': pd.read_excel
                    }
            _read_fn: Callable[[str], pd.DataFrame] = lambda fmt: _fmt_func_dict[fmt](path)
            
            _data = _read_fn(_format)
        
            _data['wht%'] = ((_data['wht']/_data['wht'].sum())*100).round(2)
            _data['cum.wht%'] = _data['wht'].cumsum()
            Sample.samples_list.append(self)
        
        return (_name, _data)
    
    def get_name(self, full: bool = False) -> str:
        '''
        full: returns the full name if true.
        '''
        _short_name: str = self._name.split(".")[0].capitalize()

        return _short_name if not full else self._name      
    
    def get_data(self) -> pd.DataFrame:
        '''
        Returns the sample dataa as a DataFrame.
        '''
        return self._data