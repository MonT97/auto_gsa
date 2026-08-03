"""
Creating, storing and retrieving default values.
"""
import json
import os
from typing import Type, TypeVar, cast, Final

from typedefs import DefaultObj, SaveObject

# Constants
# color:
DEFAULT_CLR = '#1f7bb4'

# file permission:
FULL_PERMISSION: Final[int] = 0o700
READ_ONLY: Final[int] = 0o400

T = TypeVar('T', bound=DefaultObj)

_objs: dict = {}
_cnfg_dir: str = 'auto_gsa'
_defaults_file_name: str = 'defaults.json'
_app_data_path: str = os.environ.get('LOCALAPPDATA') #type: ignore
_cnfg_dir_path: str = os.path.join(_app_data_path, _cnfg_dir)
_cnfg_file_path: str = os.path.join(_cnfg_dir_path, _defaults_file_name)

class Defaults():
    """
    A mixin wrapping the functionality to create default values.
    - functions:
    - `df_get_all`: gets all the values from the [_obj].
    - `df_get_from_file`: get the unchanged default version from the [defaults.json].
    - `df_get`: get the default value of the given class.
    """
    def _add_default(self, obj: Type[T]) -> None:
        """
        Creates the default version of the [obj] and adds it to the [_objs] list and the JSON file.
        """
        id_: str = obj.__name__

        _data = self._get_default_version(obj)
        self._write_into_file(_data, id_)

        _objs[id_] = _data

    def _get_default_version(self, obj: Type[T]) -> T:
        """
        Retrieves the default version of the provided [obj].
        """
        if obj is SaveObject:

            _data = SaveObject(
                prefix = 'results_',
                files_path  = r'D:/Documents/auto gsa data',
                results_path = r'D:/Documents/auto gsa data',
                results_dir_name = 'analysis_results',
                raw_results_dir_name = 'raw_files', #!confg
                color = DEFAULT_CLR,
                dpi = 300,
                save_raw_files = False,
                interval = (0,[]),
                transparent = False)

        return cast(T, _data)

    def _write_into_file(self, default_obj: DefaultObj, id_: str) -> None:
        """
        Writes the [default_obj] into the JSON file.
        """
        _json: dict = {}

        _dir_exist: bool = os.path.exists(_cnfg_dir_path)
        _cnfg_file_exist: bool = os.path.exists(_cnfg_file_path)

        if not _dir_exist:
             os.mkdir(_cnfg_dir_path)
        try:
            with open(_cnfg_file_path, 'r') as f:
                    _json = json.load(f)
            if default_obj.to_dict() == _json[id_]:
                return
        except Exception as e:
            _json.clear()

        _json[id_] = default_obj.to_dict()

        # Linux like [user,group,others], 4=r,2=w,1=exc,0=none.
        if _cnfg_file_exist:
            os.chmod(_cnfg_file_path, FULL_PERMISSION)

        with open(_cnfg_file_path, 'w') as f:
                json.dump(_json, f, indent=4)
                
        os.chmod(_cnfg_file_path, READ_ONLY)

    def df_get_from_file(self, obj: Type[T]):
        """
        Retrieves the default version of the provided [obj] from the `defaults.json` file.
        """
        id_: str = obj.__name__

        with open(_cnfg_file_path, 'r') as f:
            _json = json.load(f)

        def _match_type(obj: Type[T], json, id_: str) -> T:
            """
            Self documenting.
            """
            if obj is SaveObject:
                _obj = SaveObject(**json[id_])

            return cast(T, _obj)

        _obj = _match_type(obj, _json, id_)

        return _obj

    def df_get(self, obj: Type[T]) -> T:
        """
        Retrieves the default version of the provided [obj], creates it if doesn't exist.
        - obj: is the class itself [obj], not an instance [obj()].
        """
        if obj.__name__ not in _objs:
            self._add_default(obj)
            
        return _objs[obj.__name__]

    def df_get_all(self) -> dict:
        """
        Retrieves all default objects.
        """
        return _objs