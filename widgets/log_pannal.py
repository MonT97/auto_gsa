import datetime as dt
import os
import tkinter as tk

import customtkinter as ctk

from mixins import HasToolTip, Observer


class LoggingLabel(ctk.CTkFrame, HasToolTip, Observer):
    """
    CTkFrame:
    The class that handels logging various massages and saving said massages to a log file.
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        self.configure(corner_radius=0)

        self.cnfg_path: str = ''
        self.cnfg_folder_name: str = 'auto_gsa'
        self.log_file_path: str = ''
        self.log_file_name: str = 'log.txt'

        self.label: ctk.CTkLabel = ctk.CTkLabel(self, anchor='w', text='Log:')
        self.text_box: ctk.CTkTextbox = ctk.CTkTextbox(self,
                    state=ctk.DISABLED, corner_radius=0, activate_scrollbars=False)
        self.label.bind('<Double-Button-1>', lambda _: self._expand())
        self.htt_tip(self.label, 'double click to expand/shrink')

        self.label.pack(side='left', padx=5)
        self.text_box.pack(side='left', fill='both', expand=True)
        
        self._setup_log_file()

    def _setup_log_file(self) -> None:
    
        _cnfg_dir: str = os.environ.get('LOCALAPPDATA') #type: ignore
        self.cnfg_path = os.path.join(_cnfg_dir, self.cnfg_folder_name)

        if not os.path.exists(self.cnfg_path):
            os.mkdir(self.cnfg_path)

    def _log_to_file(self, text: str) -> None:
        """
        Log text into the log file.
        """
        _mode: str = 'a'
        _header: str = f'created in: {dt.datetime.now().ctime()}\n--------------<>-------------\nAuto_GSA configuration\n--------------<>-------------\n'
        
        self.log_file_path = os.path.join(self.cnfg_path, self.log_file_name)
        _file_exists: bool = os.path.exists(self.log_file_path)
        if not _file_exists: #TODO: additional conditions??
            _mode: str = 'w'
            text+=_header

        # Lunix like [user,group,others], 4=r,2=w,1=exc,0=none.
        if _file_exists:
            os.chmod(self.log_file_path, 0o700)
        with open(self.log_file_path, _mode) as f:
            f.write(text+'\n')
        os.chmod(self.log_file_path, 0o400)

    def write(self, text: str) -> None:
        """
        Write into the text box.
        """
        self.text_box.configure(state=ctk.NORMAL)
        self.text_box.insert(tk.INSERT, text)
        self.text_box.see(tk.END)
        self.text_box.insert(tk.INSERT, '\n')
        self.text_box.configure(state=ctk.DISABLED)

        self._log_to_file(text)
    
    def _expand(self) -> None:
        """
        Expands the logging widget.
        """
        # This fills the app with the this widget
        self.obs_broadcast('LoggingPanal-zoom', self, ['log'])

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