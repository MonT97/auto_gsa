from collections.abc import Callable

from mixins import Defaults, HasToolTip, Validator
from .base_screen import BaseScreen
from typedefs import FileFormat
from utils import utils

import os
import re
import customtkinter as ctk

#! Think it over!
class ImportScreen(BaseScreen, Defaults, HasToolTip, Validator):
    """
    Import dialouge screem widget.
    """
    def __init__(self, master, master_setter: Callable, path: str = '') -> None:
        super().__init__(master, title='import screen', approve_label='import', size=(430,530))

        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+500)//4,
            self.master.winfo_screenheight()//4)
        self.geometry(f'{self.size[0]}x{self.size[1]}+{self.pos[0]}+{self.pos[1]}')

        self.path: str = path
        self.prev_paths: list[str] = []
        self.next_paths: list[str] = []
        self.files_dict: dict = {}
        self.dir_list: list[str] = []
        self.filters: list[str] = []
        self.selected_files: list[str] = []

        self.entry_frame=  ctk.CTkFrame(self.main_frame)
        self.filters_frame = ctk.CTkFrame(self.main_frame)
        self.files_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.dirs_frame = ctk.CTkFrame(self.files_frame)

        # Entry frame:
        self.entry_font = ctk.CTkFont('Arial', 16)
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self.entry_frame,
                height=30, placeholder_text='sample files folder path...',
                font=self.entry_font)
        self.entry.bind("<Enter>", lambda _: self.after(1,self.entry.focus_set))
        self.entry.bind("<KeyPress-Return>", lambda _: self._import_files())
        self.htt_tip(self.entry, 'Press Enter/Return to list files to import.')

        self.nav_btns = ctk.CTkFont('Arial', 16, 'bold')
        self.up = ctk.CTkButton(self.entry_frame, text='^', width=20,
                font=self.nav_btns,
                command=lambda: self._navigate('up'), state=ctk.DISABLED)
        self.htt_tip(self.up, 'up')

        self.bck = ctk.CTkButton(self.entry_frame, text='<', width=20,
                font=self.nav_btns,
                command=lambda: self._navigate('bck'), state=ctk.DISABLED)
        self.htt_tip(self.bck, 'back')

        self.frd = ctk.CTkButton(self.entry_frame, text='>', width=20,
                font=self.nav_btns,
                command=lambda: self._navigate('frd'), state=ctk.DISABLED)
        self.htt_tip(self.frd, 'forward')

        utils.bg_transparent([self.entry_frame, self.bck, self.frd, self.up])

        self.up.pack(side='left', fill='y', padx=2, pady=2)
        self.frd.pack(side='right', fill='y', pady=2, padx=2)
        self.bck.pack(side='right', fill='y', pady=2, padx=2)
        self.entry.pack(side='left', expand=True, fill='x', pady=2)

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                text='show folder', width=150, state=ctk.DISABLED,
                command=lambda: self._on_show_btn())
        self.htt_tip(self.show_btn, 'open the results folder')

        # Filters frame:
        self.filters_font = ctk.CTkFont('Arial', 14, 'bold')
        self.select_all = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='all', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command=lambda: self._on_select_all())
        self.htt_tip(self.select_all, 'select all files')
        
        self.select_between = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='between', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command= lambda: self._toggle_filters(bool(self.select_between.get())))
        self.htt_tip(self.select_between, 'select every thing between two selections inclusively.')

        self.csv = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='csv', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command= lambda: self._filter(bool(self.csv.get()), self.csv.cget('text')))
        self.htt_tip(self.csv, 'csv files only')
        
        self.excel = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='xlsx', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command= lambda: self._filter(bool(self.excel.get()), self.excel.cget('text')))
        self.htt_tip(self.excel, 'excel files only')
        
        utils.bg_transparent([self.select_all, self.csv, self.excel])

        self.csv.pack(side='left', expand=True, fill='x', padx=2)
        self.excel.pack(side='left', expand=True, fill='x', padx=2)
        self.select_all.pack(side='left', expand=True, fill='x', padx=2)
        self.select_between.pack(side='left', expand=True, fill='x', padx=2)

        self.approve_btn.configure(font=self.entry_font)
        self.cancel_btn.configure(font=self.entry_font)
        self.approve_btn.configure(command= lambda: self._on_approve(master_setter))

        self.entry_frame.pack(side='top', fill='x')
        self.filters_frame.pack(side='top', fill='x', pady=5)

        if path:
            _end: int = len(self.path)
            self._update_entry_and_import(_end)

    def _import_files(self, filter_: list[str] = []) -> None:
        """
        Displays directories and valid files found in [self.path].
        - filter_: format based filtering, uses format from FileFormat enum.
        """
        if self.path != self.entry.get():
            self.path = self.entry.get()

            self.prev_paths.clear()
            self.next_paths.clear()
        
        #TODO: error handeling, pop up, or the typical log maybe?!
        if not os.path.exists(self.path):
            return
        
        filter_ = [format_.value for format_ in FileFormat] if not filter_ else filter_

        self.select_all.deselect()
        self.select_between.deselect()

        self.selected_files.clear()

        # Clean frames:
        if self.dirs_frame.pack_slaves():
            for i in self.dirs_frame.pack_slaves():
                i.pack_forget()

        if self.files_frame.pack_slaves():
            for i in self.files_frame.pack_slaves():
                i.pack_forget()
            self.files_dict.clear()

        # Find dirs and valid files:
        _children: list[str] = os.listdir(self.path)

        _get_dir_path: Callable = lambda x: os.path.isdir(os.path.join(self.path, x))
        _dirs: list[str] = [i for i in _children if _get_dir_path(i)]
        
        _validate: Callable = lambda x,y,z: self.val_samples(x, y) and y.split('.')[-1] in z
        _files: list[str] = [_file for _file in _children if _validate(self.path, _file, filter_)]
        
        # Fill-in dirs and valid files:
        for _dir in _dirs:
            _frame = ctk.CTkFrame(self.dirs_frame, height=25)
            _dir_btn = ctk.CTkButton(_frame, text=_dir)
            _dir_btn.configure(command=lambda x=_dir_btn.cget('text'): self._go_to_dir(x))

            _dir_btn.pack(side='top', expand=True, fill='x')
            _frame.pack(fill='x', pady=2, padx=2)

            utils.bg_transparent(_dir_btn)

        if _dirs:
            self.dirs_frame.pack(side='top', expand=True, fill='x')

        for file_ in _files:
            _frame = ctk.CTkFrame(self.files_frame, height=25)
            _file_btn = ctk.CTkCheckBox(_frame, state=ctk.NORMAL, checkbox_height=20,
                    text='', checkbox_width=20, border_width=2)
            _label = ctk.CTkLabel(_frame, text=file_)
            _file_btn.configure(
                    command=lambda b=(_file_btn, _label): self._select_file(b))
            utils.bg_transparent(_file_btn)

            self.files_dict[file_] = (_file_btn, _label)

            _label.place(anchor='s', relx=.5, rely=1, relheight=1)
            _file_btn.place(anchor='w', relx=.008, rely=.47, relheight=1)

            _frame.pack(side='top', fill='x', pady=2)
        
        # Layout:
        self.show_btn.configure(command=lambda: self._on_show_btn())
        self.show_btn.configure(state=ctk.NORMAL)
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        
        self.files_frame.pack(side='top', expand=True, fill='both', padx=5, pady=5)  

        self._update_nav_btns()      

    def _go_to_dir(self, dir_: str) -> None:
        """
        Change directory to [dir_]
        """
        _end: int = len(self.path)
        self.prev_paths.append(self.path)
        self.path = os.path.join(self.path, dir_)
        
        self._update_entry_and_import(_end)
        self._update_nav_btns()

    def _navigate(self, flag: str) -> None:
        """
        Navigate up or down the file system.
        """
        _end: int = len(self.path)
        
        if flag == 'up':
            self.next_paths.append(self.path)
            self.path = os.path.split(self.path)[0]
        elif flag == 'bck':
            self.next_paths.append(self.path)
            self.path = self.prev_paths.pop(-1)
        else:
            self.prev_paths.append(self.path)
            self.path = self.next_paths.pop(-1)

        self._update_entry_and_import(_end)
        self._update_nav_btns()
    
    def _update_entry_and_import(self, end: int) -> None:
        """
        Updates [self.entry] text to the new path.
        - end: The length of [self.path] before the modification which necessitated the update.
        """
        self.entry.delete(0,end)
        self.entry.insert(0, self.path)
        self._import_files()

    def _update_nav_btns(self) -> None:
        """
        Handles the state of the two navigation buttons, [self.bck] and [self.frd].
        """
        _at_drive_root: Callable = lambda x: bool(re.match(r'^\W+$', os.path.splitdrive(x)[-1]))
        
        if _at_drive_root(self.path):
            self.up.configure(state=ctk.DISABLED)
        else:
            if self.up.cget('state') == ctk.DISABLED:
                self.up.configure(state=ctk.NORMAL)
            
        if not self.prev_paths:
            self.bck.configure(state=ctk.DISABLED)
        else:
            if self.bck.cget('state') == ctk.DISABLED:
                self.bck.configure(state=ctk.NORMAL)
        
        if not self.next_paths:
            self.frd.configure(state=ctk.DISABLED)
        else:
            if self.frd.cget('state') == ctk.DISABLED:
                self.frd.configure(state=ctk.NORMAL)

    def _toggle_filters(self, _flag: bool) -> None:
        """
        Tggles the filters On/Off according to the given [flag].
        """
        if _flag:
            self.csv.configure(state=ctk.DISABLED)
            self.excel.configure(state=ctk.DISABLED)
        else:
            self.csv.configure(state=ctk.NORMAL)
            self.excel.configure(state=ctk.NORMAL)

    def _on_select_all(self) -> None:
        """
        Select/deselect all files.
        """
        _flag: bool = bool(self.select_all.get())
        
        self.select_between.deselect()

        for _, data in self.files_dict.items():
            btn = data[0]
            if _flag:
                if not btn.get():
                    btn.toggle()
                self.select_all.configure(text='clear all')
                self.select_between.configure(state=ctk.DISABLED)
                self._toggle_filters(_flag)
            else:
                if btn.get():
                    btn.toggle()
                self.select_all.configure(text='all')
                self.select_between.configure(state=ctk.NORMAL)
                self._toggle_filters(_flag)

    def _filter(self, state: bool, filter_: str) -> None:
        """
        Filters the files using the given [filter].
        """
        self.selected_files.clear()

        if state and filter_ not in self.filters:
            self.filters.append(filter_)
        else:
            self.filters.remove(filter_)

        self._import_files(self.filters)

    def _select_file(self, data: tuple[ctk.CTkCheckBox, ctk.CTkLabel]) -> None:
        """
        Self documenting name, triggered when a file is checked.
        """
        _btn, _label = data
        _state: bool = bool(_btn.get())
        _file_name: str = _label.cget('text')
        _key_list: list [str] = list(self.files_dict.keys())
        _can_tween: bool = bool(self.selected_files) and (bool(self.select_between.get()))
        
        if _state:
            self.selected_files.append(_file_name)
            if _can_tween:
                _start: int = min([_key_list.index(i) for i in self.selected_files])
                _end: int = max([_key_list.index(i) for i in self.selected_files])+1
                
                self.selected_files = _key_list[_start:_end]

                for file_ in self.selected_files:
                    _btn = self.files_dict[file_][0]
                    _btn.select()
        else:
            self.selected_files.remove(_file_name)
    
    def _on_show_btn(self) -> None:
        """
        Opens the latest current path [self.path] in the file explorer.
        """
        os.startfile(self.path)

    def _on_approve(self, setter: Callable) -> None:
        """
        Calls the master prvided [setter] function.
        """
        setter(self.entry.get(), sorted(self.selected_files))