'''
Creating and retrieving default values.
'''
from typedefs import SaveObject

import os
import json

class Defaults():
    '''
    A mixin wrapping the functionality to create default values.
    '''
    _objs: dict = {}

    def _initial_setup(self) -> None:
        '''
        As the name says.
        '''
        self._id: str = ''

        _cnfg_folder_name: str = 'auto_gsa'
        _defaults_file_name: str = 'defaults.json'
        _app_data_path: str = os.environ.get('LOCALAPPDATA') #type: ignore

        self._cnfg_path: str = os.path.join(_app_data_path, _cnfg_folder_name)
        self._cnfg_file_path: str = os.path.join(self._cnfg_path, _defaults_file_name)

        def _create_file() -> None:
            '''
            Creates the defaults file path.
            '''
            if not os.path.exists(self._cnfg_file_path):
                os.mkdir(self._cnfg_file_path)

        if os.path.exists(self._cnfg_path): return
        _create_file()

    def _add_default(self, obj) -> None:

        self._initial_setup()

        id_: str = obj.__class__.__qualname__

        data = self._populate_defaults(obj)
        self._write_into_file(data, id_)

        self._objs[id_] = data

    def _populate_defaults(self, obj):
        
        type_ = type(obj)

        if type_ is SaveObject:
            
            _data = SaveObject()
            _data.prefix = 'resutls_'
            _data.results_path = 'd:/documents/auto gsa data'
            _data.results_folder_name = 'analysis_results'
            _data.color = '#1f7bb4'
            _data.interval = tuple()

        return _data

    def _write_into_file(self, obj, id_) -> None:

        _json_obj = {f'{id_}': obj.to_dict()}

        with open(self._cnfg_file_path, 'w') as f:
                _json = json.dumps(_json_obj, indent=4)
                f.write(_json)

    def df_get_default_from_file(self, obj):
        '''
        Retieves the default version of the provided [obj] from the defaults.json file.
        '''
        self._initial_setup()
        with open(self._cnfg_file_path, 'r') as f:
            _json = json.load(f)

        return _json[obj.__class__.__qualname__]

    def df_get_default(self, obj):
        '''
        Retieves the default version of the provided [obj], however, if doesn't exist, it creates it.
        '''
        if not obj.__class__.__qualname__ in list(self._objs.keys()):
            self._add_default(obj)
            
        return self._objs[obj.__class__.__qualname__]

    def df_get_all(self) -> dict:

        return self._objs
