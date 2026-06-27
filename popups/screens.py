"""
Pop-up screens.
"""
from collections.abc import Callable

from .pickers import BasePicker, IntervalPicker, GraphColorPicker, SaveRawsPicker
from mixins import Defaults, HasToolTip, Validator
from typedefs import SaveObject, FileFormat
from utils import utils

import os
import customtkinter as ctk

class BaseScreen(ctk.CTkToplevel, HasToolTip):
    """
    The Base screen class.
    """
    def __init__(self, master, title: str = 'Title',
                 approve_label: str = 'approve', cancel_label: str = 'close',
                 size: tuple[int,int] = (450,300)) -> None:
        super().__init__(master)
        self.size = size
        self.title(title)
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.geometry(f"{self.size[0]}x{self.size[1]}")

        self.bind('<Enter>', lambda _: self.focus_set())

        self.main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self, height=30)

        self.approve_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=approve_label, width=150)

        self.cancel_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text=cancel_label, width=150, command= lambda: self.close())

        self.cancel_btn.place(anchor='w', relx=0, rely=.5, relwidth=.2, relheight=1)
        self.approve_btn.place(anchor='e', relx=1, rely=.5, relwidth=.2, relheight=1)

        self.main_frame.place(anchor='n', relx=.5, rely=.025, relwidth=.975, relheight=.825)
        self.button_frame.place(anchor='s', relx=.5 ,rely=.975, relwidth=.975, relheight=.1)

        self.after(200, lambda: self.iconbitmap('assets/default.ico'))

    def close(self) -> None:
        """
        Closes the window.
        """
        self.destroy()

#! Think it over!
class ImportScreen(BaseScreen, Defaults, HasToolTip, Validator):
    """
    Import dialouge widget.
    """
    def __init__(self, master, master_setter: Callable, path: str = '') -> None:
        super().__init__(master, title='import', approve_label='import')

        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+500)//4,
            self.master.winfo_screenheight()//4)
        self.geometry(f'{self.size[0]}x{self.size[1]}+{self.pos[0]}+{self.pos[1]}')

        self.path: str = ''
        self.files_dict: dict = {}
        self.filters: list[str] = []
        self.selected_files: list[str] = []

        self.files_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.filters_frame = ctk.CTkFrame(self.main_frame)
               
        self.entry: ctk.CTkEntry = ctk.CTkEntry(self.main_frame,
                height=30, placeholder_text='sample files folder path...')
        if path: self.entry.insert(0, path)
        self.entry.bind("<Enter>", lambda _: self.after(1,self.entry.focus_set))
        self.entry.bind("<KeyPress-Return>", lambda _: self._import_files())

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self._on_show_btn())
        self.htt_tip(self.show_btn, 'open the results folder')

        # Filters:
        self.select_all = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='All', checkbox_height=18, checkbox_width=18,
                border_width=2)
        self.htt_tip(self.select_all, 'select all files')

        self.csv = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='csv', checkbox_height=18, checkbox_width=18,
                border_width=2,
                command= lambda: self._filter(bool(self.csv.get()), self.csv.cget('text')))
        self.htt_tip(self.csv, 'csv files only')
        
        self.excel = ctk.CTkCheckBox(self.filters_frame,
                state=ctk.NORMAL, text='xlsx', checkbox_height=18, checkbox_width=18,
                border_width=2,
                command= lambda: self._filter(bool(self.excel.get()), self.excel.cget('text')))
        self.htt_tip(self.excel, 'excel files only')
        
        utils.bg_transparent([self.select_all, self.csv, self.excel])

        self.csv.pack(side='left', expand=True, fill='x', padx=2)
        self.excel.pack(side='left', expand=True, fill='x', padx=2)
        self.select_all.pack(side='left', expand=True, fill='x', padx=2)

        self.approve_btn.configure(command= lambda: self._on_approve(master_setter))

        self.entry.pack(side='top', fill='x')
        self.filters_frame.pack(side='top', fill='x', pady=5, padx=5)

    def _import_files(self, filter_: list[str] = []) -> None:
        """
        Populates the [self.entry] with validatedf files.
        """
        if not filter_:
            filter_ = [format_.value for format_ in FileFormat]

        self.select_all.deselect()
        self.path = self.entry.get() if self.path != self.entry.get() else self.path
    
        if not os.path.exists(self.path):
            return

        if self.files_frame.slaves():
            for i in self.files_frame.slaves():
                i.pack_forget()
            self.files_dict.clear()
        
        _validate: Callable = lambda x,y,z: self.val_samples(x, y) and y.split('.')[-1] in z
        _files: list[str] = [_file for _file in os.listdir(self.path) if _validate(self.path, _file, filter_)]

        for file_ in _files:
            _frame = ctk.CTkFrame(self.files_frame, height=25)
            _file_btn = ctk.CTkCheckBox(_frame, state=ctk.NORMAL, checkbox_height=25,
                text='', checkbox_width=25, border_width=2)
            _label = ctk.CTkLabel(_frame, text=file_)
            _file_btn.configure(
                command=lambda b=(_file_btn, _label): self._select_file(b))

            self.files_dict[f'{file_}'] = (_file_btn, _label)

            _file_btn.place(anchor='w', relx=0, rely=.5, relheight=1)
            _label.place(anchor='s', relx=.5, rely=1, relheight=1)

            _frame.pack(fill='x', pady=2)
        
        self.show_btn.configure(command=lambda: self._on_show_btn())
        self.show_btn.configure(state=ctk.NORMAL)

        self.files_frame.pack(side='top', expand=True, fill='x', padx=5, pady=5)        
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)

    def _on_select_all(self) -> None:
        
        for _, data in self.files_dict.items():
            btn = data[0]
            btn.toggle()

    def _filter(self, state: bool, filter_: str) -> None:
    
        if state and filter_ not in self.filters:
            self.filters.append(filter_)
        else:
            self.filters.remove(filter_)

        self._import_files(self.filters)

    def _select_file(self, data: tuple[ctk.CTkCheckBox, ctk.CTkLabel]) -> None:
        """
        Self documenting name.
        """
        btn, label = data
        _state: bool = bool(btn.get())
        _file_name: str = label.cget('text')

        if _state:
            self.selected_files.append(_file_name)
        else:
            self.selected_files.remove(_file_name)
    
    def _on_show_btn(self) -> None:
        """
        Opens the latest results folder in the file explorer.
        """
        os.startfile(self.path)

    def _on_approve(self, setter: Callable) -> None:
        """
        Calls the prvided [setter] function.
        """
        setter(self.entry.get(), self.selected_files)


#TODO: a way to remember what we did before, a running singlton of sorts; LTS.
class ExportScreen(BaseScreen, Defaults, HasToolTip):
    """
    The export confirmation dialougue widget.
    """
    def __init__(self, master, use_global_defaults: bool = False) -> None:
        super().__init__(master, title='export', approve_label='export')
        self.master = master
        self.use_global_defaults: bool = use_global_defaults
        self.approve_btn.configure(command=self._on_approve)

        #This is a hard coded value; trail&error driven.
        self.pos: tuple[int,int] = (
            (self.master.winfo_screenwidth()+500)//4,
            self.master.winfo_screenheight()//4)
        
        self.geometry(f'{self.size[0]}x{self.size[1]}+{self.pos[0]}+{self.pos[1]}')

        self.params: SaveObject = self.df_get(SaveObject) if not use_global_defaults else self.df_get_from_file(SaveObject)
    
        self.default_color: str = self.params.color #TODO: universaize!

        self.show_btn: ctk.CTkButton = ctk.CTkButton(self.button_frame,
                    text='show folder', width=150, state=ctk.DISABLED,
                    command=lambda: self.on_show_btn())

        self.prfx_pckr: BasePicker = BasePicker(self.main_frame, 'Prefix', self.params.prefix)
        self.folder_name_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Folder name', self.params.results_folder_name)
        self.results_path_pckr: BasePicker = BasePicker(
                    self.main_frame, 'Path', self.params.results_path)
        self.graph_clr_pckr: GraphColorPicker = GraphColorPicker(self.main_frame)  
        self.sample_pckr: IntervalPicker = IntervalPicker(self.main_frame)
        self.raws_pckr: SaveRawsPicker = SaveRawsPicker(self.main_frame,
                    'Export raw/un-interpreted spreadsheets.')

        self.sample_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.raws_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.prfx_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.results_path_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.folder_name_pckr.pack(expand=True, fill='x', padx=2, pady=2)
        self.graph_clr_pckr.pack(expand=True, fill='x', padx=2, pady=2)

    def set_limit(self, val: int) -> None:
        """
        Sets the interval cap, which is the number of active samples.
        """
        self.sample_pckr.set_upper_limit(val)

    def set_color(self, color: str) -> None:
        """
        Sets the color.
        """
        self.graph_clr_pckr.color = color

    def _on_approve(self) -> None:
        """
        Sets the SaveObj.
        """
        self.params.prefix = self.prfx_pckr.get_value()
        self.params.results_path = self.results_path_pckr.get_value()
        self.params.results_folder_name = self.folder_name_pckr.get_value()
        self.params.interval  = self.sample_pckr.get_value()
        self.params.color = self.graph_clr_pckr.color if self.graph_clr_pckr.get_value() else self.default_color
        self.params.save_raw_files = self.raws_pckr.get_value()
        # As the toplevel() from a ctk.TopLevel isn't the same, so, master is needed!
        self.master.winfo_toplevel().event_generate("<<Screens-saved>>")

    def set_results_path(self, path: str) -> None:
        """
        Outside signal triggered, when export is complete.
        - path[str]: the reults folder path. 
        """
        self.results_path: str = path
        self.show_btn.configure(state=ctk.NORMAL)
        self.show_btn.place(anchor='n', relx=.5, rely=0, relwidth=.20, relheight=1)
        self.htt_tip(self.show_btn, 'open the results folder')

    def on_show_btn(self) -> None:
        """
        Opens the latest results folder in the file explorer.
        """
        os.startfile(self.results_path)

    def get_params(self) -> SaveObject:
        """
        Returns the SaveObj.
        """
        return self.params