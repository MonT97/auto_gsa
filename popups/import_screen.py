# BaseWidget is necessitated by the need to emit/broadcast signals.
import os
from collections.abc import Callable
from tkinter import BaseWidget
from tkinter.filedialog import Open

from mixins import Observer
from typedefs import FileFormat, LogMsgType, Signal


class ImportScreen(Open, BaseWidget, Observer):
    """
    Import dialogue screen widget.
    """
    _formats: list[str] = [i.value for i in FileFormat]

    _types: list[tuple[str, list|str]] = [
        ('All data files', _formats),
        ('Comma separated values', f'.{FileFormat.CSV.value}'),
        ('Excel file', f'.{FileFormat.EXCEL.value}')
        ]
    
    def __init__(self, master, path: str,
                 connection_function: Callable[[str,list[str]],None], multiple: bool =True) -> None:
        """
        Import dialogue screen widget.
        - `path`: the path to look into.
        - `connection_func`: function to call on approve.
        - `multiple`: enables multi-file selection.
        """
        self._title: str = 'Select sample files'
        self._defaultextension: str = FileFormat.CSV.value

        super().__init__(master=master,
            title=self._title,
            initialdir=path,
            defaultextension=self._defaultextension, 
            filetypes=self._types,
            multiple=multiple)

        self.show(connection_function)

    def __repr__(self) -> str:
        return f'{__class__} title: {self._title}'

    def show(self, func: Callable[[str,list[str]],None]) -> None:
        """
        Show the dialogue screen.
        """
        _files_list: list[str] = super().show()
        _get_file_name: Callable[[str],str] = lambda x: os.path.split(x)[-1]

        if not _files_list:
            self.obs_broadcast(Signal.LOG, self, ('No Files where picked!', LogMsgType.WARNING))
            return
        
        _path: str = os.path.split(_files_list[0])[0]
        _files_list = [_get_file_name(i) for i in _files_list]

        func(_path, _files_list)