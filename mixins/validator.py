from typedefs import FileFormat
from models import Sample

import os
import pandas as pd

from typing import Callable

class Validator():
    """
    Rsoponsible for validating data.
    """
    def val_samples(self, samples_dir_path: str, sample_file_name: str) -> bool:
        """
        Validates the sample file format and the sample data within.
        - ** for now it's just a format validator.
        """
        _valid_sample: bool = False

        _fomrat: str = sample_file_name.split('.')[-1]
        _supported_formats: list[str]  = [format_.value for format_ in FileFormat]

        _valid_format = _fomrat in _supported_formats

        #TODO: add sample data validation:
    #    if _valid_format:
            # _sample = Sample(os.path.join(samples_dir_path, sample_file_name))

        _valid_sample = _valid_format

        return (_valid_sample)
    
    def val_handle_aio(self, sample_dir_path: str, sample_file_name: str) -> list[str]:
        
        _format: str = sample_file_name.split('.')[-1]
        _path: str = os.path.join(sample_dir_path, sample_file_name)

        _kw = {'xlsx':{'engine':'openpyxl', 'header': None},
                   'csv':{}}
        _fnc_dict: dict[str, Callable] = {
                'csv': pd.read_csv,
                'xlsx': pd.read_excel
                }
        _read_fn: Callable[[str], pd.DataFrame] = lambda fmt:_fnc_dict[fmt](_path, **_kw[fmt])
        
        _df: pd.DataFrame = _read_fn(_format)
        
        _is_aio: bool = min(_df.shape) > 2

        _nms: list[str] = [sample_file_name]

        if _is_aio:
            # assume data is in the top left corner of the spread sheet:
            # r: row, c: column

            # index of the first (na) value:
            _frst_r: int = _df.isna().idxmax(0).max()
            _frst_r = _df.shape[0] if _frst_r == 0 else _frst_r
            _frst_c: int = _df.isna().idxmax(1).max()
            _frst_c = _df.shape[1] if _frst_c == 0 else _frst_c

            _df = _df.iloc[:_frst_r, :_frst_c]

            # assume it's row wise, sample per each row:
            _assume_r = _df.iloc[0,:]         # assume first row is phi sizes.
            _strip_na: Callable[[pd.Series],pd.Series] = lambda x: x[x.str.contains('[a-z]').isna()]
            # any phi series must contain values between shown limits.
            # hard coded, due to real sieve set limitations.
            _is_phi: Callable[[pd.Series], bool] = lambda x: not (x.between(-6.75,6.75).empty)

            _row_wise = _is_phi(_strip_na(_assume_r))
            if _row_wise:
                _df = _df.T
            
            _df_num = _df.iloc[1:,:].copy()
            _nsmpls: int = _df_num.shape[1]
            _padding: int = len(f'{_nsmpls}')
            #would propably need reworking, what if we have only numerical sample names?
            _has_names = bool(_df.iloc[0,:].str.contains(r'[a-z]').any())
            if _has_names:
                _nms = [f'{i}.csv' for i in _df.iloc[0,1:]]
            else:
                _nms = [f'sample_{i:0{_padding}}.csv' for i in range(1,_df_num.shape[1])]
            
            _get_sample = lambda i: _df_num.iloc[:,[0,i]].rename(columns={0: 'phi', i: 'wht'})
            
            _samples_list: list[pd.DataFrame] = [_get_sample(i) for i in range(1,_nsmpls)]
            _samples_dict: dict[str, pd.DataFrame] = {
                        nm: data for nm, data in zip(_nms, _samples_list)
                        }
            
            # unpack aio data into disk:
            #TODO: should we make a temp cache insted of disc?!!, or maybe too complex?
            for name, data in _samples_dict.items():
                _path = os.path.join(sample_dir_path, name)
                data.to_csv(_path, index=False)
        
        return _nms