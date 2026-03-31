"""
Creating, storing and retrieving default values.
"""
from typing import TypeVar, Type, cast

from typedefs import DefaultObj, SaveObject

import os
import json

T = TypeVar('T', bound=DefaultObj)

class Defaults():
    """
    A mixin wrapping the functionality to create default values.
    """
    _objs: dict = {}
    _cnfg_folder_name: str = 'auto_gsa'
    _defaults_file_name: str = 'defaults.json'
    _app_data_path: str = os.environ.get('LOCALAPPDATA') #type: ignore
    _cnfg_path: str = os.path.join(_app_data_path, _cnfg_folder_name)
    _cnfg_file_path: str = os.path.join(_cnfg_path, _defaults_file_name)

    def _add_default(self, obj: Type[T]) -> None:
        """
        Creates the default version of the [obj] and adds it to the [_objs] list and the JSON file.
        """
        id_: str = obj.__name__

        _data = self._get_default_version(obj)
        self._write_into_file(_data, id_)

        self._objs[id_] = _data

    def _get_default_version(self, obj: Type[T]) -> T:
        """
        Retrieves the default version of the provided [obj].
        """
        if obj is SaveObject:

            _data = SaveObject()
            _data.prefix = 'resutls_'
            _data.results_path = 'd:/documents/auto gsa data'
            _data.results_folder_name = 'analysis_results'
            _data.color = '#1f7bb4'
            _data.raw_files = False
            _data.interval = (0,0)

        return cast(T, _data)

    def _write_into_file(self, default_obj, id_: str) -> None:
        """
        Writes the [default_obj] into the JSON file.
        """
        _json: dict = {}

        try:
            with open(self._cnfg_file_path, 'r') as f:
                    _json = json.load(f)
            if id_ in _json: return
        except Exception as e:
            _json.clear()

        _json[f'{id_}'] = default_obj.to_dict()

        with open(self._cnfg_file_path, 'w') as f:
                json.dump(_json, f, indent=4)

    def df_get_from_file(self, obj: Type[T]):
        """
        Retieves the default version of the provided [obj] from the defaults.json file.
        """
        id_: str = obj.__name__

        with open(self._cnfg_file_path, 'r') as f:
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
        Retrieves the default version of the provided [obj] and creates it if doesn't exist.
        - obj: is the class itself [obj], not an instanse [obj()].
        """
        if not obj.__name__ in list(self._objs.keys()):
            self._add_default(obj)
            
        return self._objs[obj.__name__]

    def df_get_all(self) -> dict:
        """
        Retrieves all default objects.
        """
        return self._objs