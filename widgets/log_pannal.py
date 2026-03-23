import os

from tktooltip import ToolTip

import customtkinter as ctk
import tkinter as tk 
import datetime as dt

class LoggingLabel(ctk.CTkFrame):
    '''
    CTkFrame:
    The class that handels logging various massages and saving said massages to a log file.
    '''
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        self.configure(corner_radius=0)

        self.cnfg_path: str = ''
        self.log_file_path: str = ''
        self.log_file_name: str = 'log.txt'

        self.label: ctk.CTkLabel = ctk.CTkLabel(self, anchor='w', text='Log:')
        self.text_box: ctk.CTkTextbox = ctk.CTkTextbox(self,
                    state=ctk.DISABLED, corner_radius=0, activate_scrollbars=False)
        self.label.bind('<Double-Button-1>', lambda _: self._open_file())
        ToolTip(self.label, msg='double click to expand', bg='#1b1e1e', fg='#ffffff', delay=1.2)

        self.label.pack(side='left', padx=5)
        self.text_box.pack(side='left', fill='both', expand=1)
        
        self._setup_log_file()

    def _setup_log_file(self) -> None:
    
        _cnfg_folder_name: str = 'auto_gsa'
        _cnfg_dir: str = os.environ.get('LOCALAPPDATA') #type: ignore
        self.cnfg_path = os.path.join(_cnfg_dir, _cnfg_folder_name)

        if not os.path.exists(self.cnfg_path):
            os.mkdir(self.cnfg_path)

    def _log_to_file(self, text: str) -> None:
        '''
        Log text into the log file.
        '''
        _text: str = text
        _mode: str = 'a'
        _header: str = f'created in: {dt.datetime.now().ctime()}\n--------------<>-------------\nAuto_GSA configuration\n--------------<>-------------\n\n\n'
        
        self.log_file_path = os.path.join(self.cnfg_path, self.log_file_name)

        if not os.path.exists(self.log_file_path): #TODO: additional conditions??
            _mode: str = 'w'
            _text: str = _header+text

        with open(self.log_file_path, _mode) as f:
            f.write(_text+'\n')

    def write(self, text: str) -> None:
        '''
        Write into the text box.
        '''
        self.text_box.configure(state=ctk.NORMAL)
        self.text_box.insert(self.text_box.index(tk.INSERT), text)
        self.text_box.see(tk.END)
        self.text_box.insert(self.text_box.index(tk.INSERT), '\n')
        self.text_box.configure(state=ctk.DISABLED)

        self._log_to_file(text)
    
    def _open_file(self) -> None:
        '''
        Open the logging file in notepad.
        '''
        # This fills the app with the this widget
        self.winfo_toplevel().event_generate("<<LoggingPanal-zoom>>")

    def on_close(self) -> None:
        '''
        Run on application closure.
        '''
        self._log_to_file('session terminated.\n--------------<>-------------\n')