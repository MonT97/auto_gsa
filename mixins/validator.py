import os

import pandas as pd

from typedefs import FileFormat
from utils import utls

# Constants:
# phi values:
MAX_SIEVE_SIZE: float = -6.75 # in phi scale [-log2(mm)].
MIN_SIEVE_SIZE: float = 6.75

# headers:
SAMPLE_HEADER: tuple = ('phi', 'wht', 'wht%', 'cum.wht%')


class Validator():
    """
    Rsoponsible for validating data.
    """
    def val_samples(self, samples_dir_path: str, sample_file_name: str) -> bool:
        """
        Validates the sample file format and the sample data within.
        - ** for now it's just a format validator.
        """
        #! It seems we don't need to check the data within; as the <=2 heuristic invalidates aio, Other ways seems impractical as a spreadsheet can take many a form!, PONDER!, if you need to re-implement, check commit 43 I think.
        _valid_sample: bool = False

        _fmt: str = sample_file_name.split('.')[-1]
        _supported_formats: list[str]  = [format_.value for format_ in FileFormat]

        _valid_format = _fmt in _supported_formats
        
        _valid_sample = _valid_format

        return _valid_sample
    
    def val_handle_aio(self, sample_dir_path: str, sample_file_name: str) -> list[str]:
        """
        Check if the file is an AIO one, if so unpacks it.
        * Must be called after [val_samples] on the same [args].
        """
        _fmt: str = sample_file_name.split('.')[-1]
        _path: str = os.path.join(sample_dir_path, sample_file_name)
        
        _df: pd.DataFrame = utls.import_form_path(_path, _fmt)
        
        _nms: list[str] = [sample_file_name]
        
        _is_aio: bool = min(_df.shape) > 2

        if _is_aio:
            # assume data is in the top left corner of the spread sheet:
            # index of the first (na) value, r:row, c:col :
            _frst_r: int = _df.isna().idxmax(0).max()
            _frst_r = _df.shape[0] if _frst_r == 0 else _frst_r
            _frst_c: int = _df.isna().idxmax(1).max()
            _frst_c = _df.shape[1] if _frst_c == 0 else _frst_c

            _df = _df.iloc[:_frst_r, :_frst_c]

            # assume it's col wise, sample per each col:
            _assume_c = _df.iloc[:,0][_df.iloc[:,0].str.contains('[a-z]').isna()]
            # any phi series must contain values [between] sieve size limits.
            _assume_c_lmtd = _assume_c.between(MAX_SIEVE_SIZE,MIN_SIEVE_SIZE)
            _col_is_phi: bool = (_assume_c_lmtd.all()) and not (_assume_c_lmtd.empty)

            if not _col_is_phi:
                _df = _df.T
            
            _df_num = _df.iloc[1:,:].copy()
            _nsmpls: int = _df_num.shape[1]
            _padding: int = len(f'{_nsmpls}')

            # would propably need reworking, what if we have only numerical sample names?
            _has_names = bool(_df.iloc[0,:].str.contains(r'[a-z]').any())
            if _has_names:
                _nms = [f'{i}.csv' for i in _df.iloc[0,1:]]
            else:
                _nms = [f'sample_{i:0{_padding}}.csv' for i in range(1,_df_num.shape[1])]
            
            _get_sample = lambda i: _df_num.iloc[:,[0,i]].rename(
                        columns={0: SAMPLE_HEADER[0], i: SAMPLE_HEADER[1]})
            
            _samples_list: list[pd.DataFrame] = [_get_sample(i) for i in range(1,_nsmpls)]
            _samples_dict: dict[str, pd.DataFrame] = {
                        nm: data for nm, data in zip(_nms, _samples_list)
                        }
            
            # unpack aio data into disk:
            #TODO: should we make a temp cache insted of disc?!!, or maybe too complex?, leaning against this idea for now!.
            for name, data in _samples_dict.items():
                _path = os.path.join(sample_dir_path, name)
                data.to_csv(_path, index=False)
        
        return _nms