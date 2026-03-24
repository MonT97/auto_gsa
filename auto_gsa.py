from widgets import FilePanal, AnalysisPanal, LoggingLabel
from platform import system

import customtkinter as ctk


if system() != "Windows":
    print("Running in non-Windows OS, some eyecandy won't be visible!")


class App(ctk.CTk):

    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,550)) -> None:
        super().__init__()

        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_panal: MainPanal = MainPanal(self)
        self.main_panal.pack(expand=1, fill='both')

    # TODO[LTS]: see if you can hide/handle the stuff chucked into the stdo, it seems fine now!!
    def on_closing(self) -> None:
        '''
        Triggered on application closure.
        '''
        self.quit()
        self.main_panal.on_close()
        self.destroy()

    def run(self) -> None:

        self.mainloop()


class MainPanal(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk):
        super().__init__(master)
        '''
        The main panal in the app.
        '''
        self.file_panal: FilePanal = FilePanal(self)
        self.analysis_panal: AnalysisPanal = AnalysisPanal(self)
        self.logging_label: LoggingLabel = LoggingLabel(self)
        
        self._layout()

        # Inter-widget communication <<Source-Action>>:
        self.winfo_toplevel().bind("<<FilePanal-analyze>>", lambda _: self.analyze())
        self.winfo_toplevel().bind("<<FilePanal-log>>", lambda _: self.log())
        self.winfo_toplevel().bind("<<LoggingPanal-zoom>>", lambda _: self.expand_log("log"))
        self.winfo_toplevel().bind("<<Screens-save>>", lambda _: self.save())
        self.winfo_toplevel().bind("<<AnalysisPanal-color>>", lambda _: self.set_color())

    def _layout(self) -> None:
        '''
        The original layout.
        '''
        self.zoom: bool = False

        self.file_panal.place(anchor='nw', relx=0, rely=0, relwidt=.24, relheight=.95)
        self.analysis_panal.place(anchor='ne', relx=1, rely=0, relwidt=.76, relheight=.95)
        self.logging_label.place(anchor='sw', relx=0, rely=1, relwidth=1, relheight=.05)

    def analyze(self) -> None:

        _sample, _graph_type = self.file_panal.get_analysis_data()

        self.analysis_panal.write(_sample, _graph_type)
        self.analysis_panal.draw_graphs(_sample, _graph_type)
    
    def log(self) -> None:

        _msg = self.file_panal.get_log_massage()
        self.logging_label.write(_msg)

    def expand_log(self, widget_name: str) -> None:
        # Any other widgets needs, in other words, do we need a match statment?
        def _reset_layout() -> None:
            self.file_panal.place_forget()
            self.analysis_panal.place_forget()
            self.logging_label.place_forget()

        if self.zoom:
            self._layout()
            return

        match widget_name:
            case "log":
                self.logging_label.place(anchor='sw', relx=0, rely=1, relwidth=1, relheight=.5)
                self.zoom = True
    
    def save(self) -> None:
        '''
        Triggers the saving function.
        '''
        self.file_panal.save_all()

    def set_color(self) -> None:
        '''
        Tell the save object about the graph color.
        '''
        _color: str = self.analysis_panal.get_graph_color()
        self.file_panal.set_saveobj_color(_color)
        
    def on_close(self) -> None:
        '''
        Triggerd on application closure.
        '''
        self.logging_label.on_close()


if __name__ == '__main__':
    app = App()
    app.run()