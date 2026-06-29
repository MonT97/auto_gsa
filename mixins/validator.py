import os

from typedefs import FileFormat
from models import Sample

class Validator():
    """
    Rsoponsible for validating data.
    """
    def val_samples(self, samples_dir: str, sample_file_name: str) -> bool:
        """
        Validates the sample file format and the sample data within.
        """
        _valid_sample: bool = False

        _fomrat: str = sample_file_name.split('.')[-1]
        _supported_formats: list[str]  = [format_.value for format_ in FileFormat]

        _valid_format = _fomrat in _supported_formats

        #TODO: add sample data validation:
    #    if _valid_format:
            # _sample = Sample(os.path.join(samples_dir, sample_file_name))

        _valid_sample = _valid_format

        return (_valid_sample)