from collections.abc import Callable
from PIL import Image

from mixins import Defaults, HasToolTip, Validator
from .base_screen import BaseScreen
from typedefs import FileFormat
from utils import utils

import os
import re
import customtkinter as ctk

type cache_element = tuple[str, ctk.CTkFrame, ctk.CTkCheckBox, ctk.CTkLabel, ctk.CTkLabel]

# Windows consts:
FILE_ATTRIBUTE_HIDDEN = 2
FILE_ATTRIBUTE_SYSTEM = 4

# Icons:
FILE_ICON = Image.open('assets/file_b.png')
FOLDER_ICON = Image.open('assets/folder.png')

# Fonts:
ENTRY_FONT = ('Arial', 16)
NAV_BTN_FONT = ('Arial', 16, 'bold')
FILTERS_FONT = ('Arial', 14, 'bold')

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

        # Back/Forward navigation psedu stacks:
        self.prev_paths: list[str] = []
        self.next_paths: list[str] = []
        
        self.files_dict: dict = {}
        self.filters: list[str] = []
        self.selected_files: list[str] = []
        
        # Cache:
        # TODO: Cache threshold to sittings?!
        self.cache_threshod: int = 25 # in list size
        self.cache: dict[str, list[cache_element]] = {}

        # Fonts:
        self.entry_font = ctk.CTkFont(*ENTRY_FONT)
        self.nav_btns_font = ctk.CTkFont(*NAV_BTN_FONT)
        self.filters_font = ctk.CTkFont(*FILTERS_FONT)

        # Frames:
        self.entry_frame=  ctk.CTkFrame(self.main_frame)
        self.filters_frame = ctk.CTkFrame(self.main_frame)
        self.files_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.dirs_frame = ctk.CTkFrame(self.files_frame)

        # Entry frame:
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self.entry_frame,
                height=30, placeholder_text='sample files folder path...',
                font=self.entry_font)
        self.entry.bind("<Enter>", lambda _: self.after(1,self.entry.focus_set))
        self.entry.bind("<KeyPress-Return>", lambda _: self._import_files())
        self.htt_tip(self.entry, 'Press Enter/Return to list files to import.')

        self.up = ctk.CTkButton(self.entry_frame, text='^', width=20,
                font=self.nav_btns_font,
                command=lambda: self._navigate('up'), state=ctk.DISABLED)
        self.htt_tip(self.up, 'up')

        self.bck = ctk.CTkButton(self.entry_frame, text='<', width=20,
                font=self.nav_btns_font,
                command=lambda: self._navigate('bck'), state=ctk.DISABLED)
        self.htt_tip(self.bck, 'back')

        self.frd = ctk.CTkButton(self.entry_frame, text='>', width=20,
                font=self.nav_btns_font,
                command=lambda: self._navigate('frd'), state=ctk.DISABLED)
        self.htt_tip(self.frd, 'forward')

        self.error_label = ctk.CTkLabel(self.main_frame,
                font=self.entry_font, corner_radius=5,
                wraplength=380, fg_color='#e53935')

        utils.bg_transparent([self.entry_frame, self.bck, self.frd, self.up, self.error_label])

        self.up.pack(side='left', fill='y', padx=2, pady=2)
        self.frd.pack(side='right', fill='y', pady=2, padx=(0,2))
        self.bck.pack(side='right', fill='y', pady=2, padx=(2,0))
        self.entry.pack(side='left', expand=True, fill='x', pady=2)

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                text='show folder', width=150, state=ctk.DISABLED,
                command=lambda: self._on_show_btn())
        self.htt_tip(self.show_btn, 'open current folder')

        # Filters frame:
        self.select_all = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='all', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command=lambda: self._on_select_all())
        self.htt_tip(self.select_all, 'de/select all files')
        
        self.select_between = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='between', checkbox_height=18, checkbox_width=18,
                border_width=2, font=self.filters_font,
                command= lambda: self._toggle_filters(bool(self.select_between.get())))
        self.htt_tip(self.select_between, 'select every thing between two selections inclusively')

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

        # Element for files_frame:
        self.dir_img = ctk.CTkImage(FOLDER_ICON, size=(20,20))
        self.file_img = ctk.CTkImage(FILE_ICON, size=(20,20))

        self.csv.pack(side='left', expand=True, fill='x', padx=2)
        self.excel.pack(side='left', expand=True, fill='x', padx=2)
        self.select_all.pack(side='left', expand=True, fill='x', padx=2)
        self.select_between.pack(side='left', expand=True, fill='x', padx=2)

        self.approve_btn.configure(font=self.entry_font, state=ctk.DISABLED,
                command= lambda: self._on_approve(master_setter))
        self.cancel_btn.configure(font=self.entry_font)
        self.show_btn.configure(command=lambda: self._on_show_btn())

        self.entry_frame.pack(side='top', fill='x')
        self.filters_frame.pack(side='top', fill='x', pady=5)

        if self.path:
            self._update_entry_and_import()

    def _import_files(self) -> None:
        """
        Displays directories and valid files found in [self.path].
        - filter_: format based filtering, uses format from FileFormat enum.
        """
        
        _cache_elements: list[cache_element] = []
        _new_entry = bool(self.path != self.entry.get())
        filter_ = [format_.value for format_ in FileFormat] if not self.filters else self.filters

        def _invalid_path() -> bool:
            """
            Validates [self.path] and handles relevant widgets.
            """
            _flag = False
            _msg = f'path [{self.path}]\n is invalid or doesn\'t exist,\nenter a new path.'
            if re.match(r'^[a-z]$', self.path):
                self.path+=r':/'
                self._update_entry_and_import()
            if not os.path.exists(self.path):
                self.error_label.configure(text=_msg)
                self.error_label.pack(side='top', fill='x', padx=5)
                self.entry.select_range(0, ctk.END)
                _flag = True
            elif self.error_label.winfo_ismapped():
                self.error_label.pack_forget()
            return _flag

        def _clear_frames() -> None:
            """
            Clears the [self.dirs_frame] and [self.files_frame].
            """
            if self.dirs_frame.pack_slaves():
                for i in self.dirs_frame.pack_slaves():
                    i.pack_forget()

            if self.files_frame.pack_slaves():
                for i in self.files_frame.pack_slaves():
                    i.pack_forget()
                self.files_dict.clear()

            self.dirs_frame.pack_forget()
            self.files_frame.pack_forget()

        def _prepare_and_pack(cache_element: cache_element, last_to_pack: bool) -> None:
            """
            Houses shared functionality in both cases, cached and non cached.
            - cache_element: tuple housing needed data, file_name, frame, button, label, img.
            - last_to_pack: for layout aesthetic purposes.
            """
            file_, frame, btn, label, img = cache_element
            utils.bg_transparent([btn, label])

            self.files_dict[file_] = (btn, label)

            _pady=(5,0) if not last_to_pack else (5,5)

            img.pack(side='left', padx=(7,5), pady=(0,1))
            label.pack(side='left', expand=True, fill='x')
            btn.pack(side='left')

            frame.pack(side='top', fill='x', pady=_pady)

        if _new_entry:
            self.path = self.entry.get()

            self.prev_paths.clear()
            self.next_paths.clear()

        # Clean selection:
        self.select_all.deselect()
        self.select_between.deselect()
        self.selected_files.clear()

        _clear_frames()

        if _invalid_path(): return

        # Handle hidden files:
        _attribs = lambda x: os.stat(os.path.join(self.path, x)).st_file_attributes
        _hidden = lambda x: _attribs(x) & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM) 
        if os.name != 'nt':
            _hidden = lambda x: x.startswith('.')
        _children: list[str] = [i for i in os.listdir(self.path) if not _hidden(i)]

        # Find dirs and valid files:
        _get_dir_path: Callable = lambda x: os.path.isdir(os.path.join(self.path, x))
        _dirs: list[str] = [i for i in _children if _get_dir_path(i)]
        
        _validate: Callable = lambda x,y,z: (self.val_samples(x, y)) and (y.split('.')[-1] in z)
        _files: list[str] = [_file for _file in _children if _validate(self.path, _file, filter_)]

        # Cache flags.
        _in_cache: bool = self.path in self.cache
        _should_cache: bool = not _in_cache and (len(_files) >= self.cache_threshod)

        # Fill-in dirs and valid files:
        for dir_ in _dirs:
            _frame = ctk.CTkFrame(self.dirs_frame, height=25)
            _img = ctk.CTkLabel(_frame, text='', image=self.dir_img)
            _dir_btn = ctk.CTkButton(_frame,text=dir_)
            _dir_btn.configure(command=lambda x=_dir_btn.cget('text'): self._go_to_dir(x))
            self.htt_tip(_dir_btn, dir_)

            _pady = (2,0) if dir_ != _dirs[-1] else (2,2)
            _img.pack(side='left', padx=(5,5), pady=2)
            _dir_btn.pack(side='left', expand=True, fill='x', padx=(0,2))
            _frame.pack(fill='x', padx=2, pady=_pady)

            utils.bg_transparent(_dir_btn)
        
        if _dirs:
            self.dirs_frame.pack(side='top', expand=True, fill='x')

        if _in_cache:
            _elements_list = [ele for ele in self.cache[self.path] if ele[0] in _files]
            
            for element in _elements_list:
                btn = element[2]
                btn.deselect()
                _prepare_and_pack(element, (element == _elements_list[-1]))

        else: 
            for file_ in _files:
                _frame = ctk.CTkFrame(self.files_frame, height=25)
                _file_btn = ctk.CTkCheckBox(_frame, state=ctk.NORMAL,
                        text='', width=20, border_width=2)
                _label = ctk.CTkLabel(_frame, text=file_)
                _img = ctk.CTkLabel(_frame, text='', image=self.file_img)
                _file_btn.configure(command=lambda b=(_file_btn, _label): self._select_file(b))
                self.htt_tip(_label, file_)
                
                _data = (file_, _frame, _file_btn, _label, _img)

                _prepare_and_pack(_data, (file_ == _files[-1]))

                if _should_cache:
                    _cache_elements.append(_data)

            if _should_cache:
                self.cache[self.path] = _cache_elements
            if _files:
                self.approve_btn.configure(state=ctk.NORMAL)                

        # Layout:
        self.show_btn.configure(state=ctk.NORMAL)
        
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        self.files_frame.pack(side='top', expand=True, fill='both', padx=5, pady=5)  

        self._update_nav_btns()      

    def _go_to_dir(self, dir_: str) -> None:
        """
        Change directory to [dir_].
        """
        self.prev_paths.append(self.path)
        self.path = os.path.join(self.path, dir_)
        
        self._update_entry_and_import()
        self._update_nav_btns()

    def _navigate(self, nave_btn_str: str) -> None:
        """
        Navigate up, forward or back the file system.
        """ 
        if nave_btn_str == 'up':
            self.next_paths.append(self.path)
            self.path = os.path.split(self.path)[0]
        elif nave_btn_str == 'bck':
            self.next_paths.append(self.path)
            self.path = self.prev_paths.pop(-1)
        else:
            self.prev_paths.append(self.path)
            self.path = self.next_paths.pop(-1)

        if self.select_all.cget('text') == 'clear all':
            self.select_all.toggle()
    
        self._update_entry_and_import()
        self._update_nav_btns()
    
    def _update_entry_and_import(self) -> None:
        """
        Updates [self.entry] text to the new path.
        - flag: if True runs _import_file() after updating.
        """
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, self.path)
        self._import_files()

    def _update_nav_btns(self) -> None:
        """
        Handles the state of the navigation buttons, [self.up], [self.bck] and [self.frd].
        """
        _at_drive_root: Callable = lambda x: bool(re.match(r'^\W+$', os.path.splitdrive(x)[-1]))
        
        if _at_drive_root(self.path):
            self.up.configure(state=ctk.DISABLED)
        else:
            self.up.configure(state=ctk.NORMAL)
            
        if not self.prev_paths:
            self.bck.configure(state=ctk.DISABLED)
        else:
            self.bck.configure(state=ctk.NORMAL)
        
        if not self.next_paths:
            self.frd.configure(state=ctk.DISABLED)
        else:
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
        _select_all = bool(self.select_all.get())
        
        self.select_between.deselect()

        for _, data in self.files_dict.items():
            btn = data[0]
            if _select_all:
                if not btn.get():
                    btn.toggle()
                    _text = 'clear all'
                    _state = ctk.DISABLED
            else:
                if btn.get():
                    btn.toggle()
                    _text = 'all'
                    _state = ctk.NORMAL

        self.select_all.configure(text=_text)
        self.select_between.configure(state=_state)
        self._toggle_filters(_select_all)

    def _filter(self, state: bool, filter_: str) -> None:
        """
        Filters the files using the given [filter].
        """
        if state and (filter_ not in self.filters):
            self.filters.append(filter_)
        else:
            self.filters.remove(filter_)

        self._import_files()

    def _select_file(self, data: tuple[ctk.CTkCheckBox, ctk.CTkLabel]) -> None:
        """
        Self documenting name, triggered when a file is checked.
        """
        _btn, _label = data
        _state = bool(_btn.get())
        _file_name: str = _label.cget('text')
        _key_list: list [str] = list(self.files_dict.keys())
        _can_tween = bool(self.selected_files) and (bool(self.select_between.get()))
        
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