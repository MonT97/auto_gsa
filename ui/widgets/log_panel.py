import datetime as dt
import os
import tkinter as tk
from typing import Final

import customtkinter as ctk

from mixins import HasToolTip, Observer
from typedefs import LogMsgType, Signal

# Constants:
# names:
CNFG_DIR_NAME: Final[str] = 'auto_gsa'
LOG_FILE_NAME: Final[str] = 'log.txt'
CNFG_DIR: Final[str|None] = os.environ.get('LOCALAPPDATA')
assert CNFG_DIR, 'Strange!, you don\'t have an appdata dir??!!'

# file permission:
FULL_PERMISSION: Final[int] = 0o700
READ_ONLY: Final[int] = 0o400


class LoggingLabel(ctk.CTkFrame, HasToolTip, Observer):
    """
    CTkFrame:
    The class that handles logging various massages and saving said massages to a log file.
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        self.configure(corner_radius=0)

        self.cnfg_path: str = ''
        self.log_file_path: str = ''

        self.label: ctk.CTkLabel = ctk.CTkLabel(self, anchor='w', text='Log:')
        self.text_box: ctk.CTkTextbox = ctk.CTkTextbox(self,
                    state=ctk.DISABLED, corner_radius=0, activate_scrollbars=False)
        self.label.bind('<Double-Button-1>', lambda _: self._expand())
        self.htt_tip(self.label, 'double click to expand/shrink')

        self.label.pack(side='left', padx=5)
        self.text_box.pack(side='left', fill='both', expand=True)
        
        self._setup_log_file()

    def _setup_log_file(self) -> None:
    
        self.cnfg_path = os.path.join(CNFG_DIR, CNFG_DIR_NAME)

        if not os.path.exists(self.cnfg_path):
            os.mkdir(self.cnfg_path)

    def _log_to_file(self, text: str) -> None:
        """
        Log [text] into the log file.
        """
        _mode: str = 'a'
        _header: str = f'created in: {dt.datetime.now().ctime()}\n---------------------------<\nAuto_GSA logfile\n>---------------------------\n'
        
        self.log_file_path = os.path.join(self.cnfg_path, LOG_FILE_NAME)
        _file_exists: bool = os.path.exists(self.log_file_path)
        if not _file_exists: #TODO: additional conditions??
            _mode: str = 'w'
            text+=_header

        # Linux like [user,group,others], 4=r,2=w,1=exc,0=none.
        if _file_exists:
            os.chmod(self.log_file_path, FULL_PERMISSION)
        with open(self.log_file_path, _mode) as f:
            f.write(text+'\n')
        os.chmod(self.log_file_path, READ_ONLY)
        
    def write(self, text: str, prefix: LogMsgType) -> None:
        """
        Write [text] into the text box.
        prefix: to append to the [text] as in [prefix]+[text].
        """
        _text: str = prefix.value + text

        self.text_box.configure(state=ctk.NORMAL)
        self.text_box.insert(tk.INSERT, _text)
        self.text_box.see(tk.END)
        self.text_box.insert(tk.INSERT, '\n')
        self.text_box.configure(state=ctk.DISABLED)

        self._log_to_file(_text)
    
    def _expand(self) -> None:
        """
        Expands the logging widget.
        """
        # This expands the app with the this widget
        self.obs_broadcast(Signal.EXPAND, self, (self,))

    def on_open(self) -> None:
        """
        Runs on application launch.
        """
        self._log_to_file(f'\nsession started [{dt.datetime.now().ctime()}].\n')

    def on_close(self) -> None:
        """
        Runs on application closure.
        """
        self._log_to_file(f'\nsession terminated [{dt.datetime.now().ctime()}].\n--------------<>-------------\n')