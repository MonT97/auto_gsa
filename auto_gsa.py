import customtkinter as ctk

in_windows:bool = True
try:
    from ctypes import windll, byref, c_int, sizeof
except Exception as e:
    in_windows = False
    print("Running in non Windows OS, some eyecandy won't be visible!!")

from widgets import FilePanal, AnalysisPanal

class App(ctk.CTk):

    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(1000,600)):
        super().__init__()

        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(1000,600)
        self.iconbitmap("icon.ico")

        self.rowconfigure(0, weight=1, uniform="a")
        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")

        self.data_panal: ctk.CTkFrame = AnalysisPanal   (self)
        self.file_picker: ctk.CTkFrame = FilePanal(self, self.data_panal)

        self.file_picker.grid(row=0, column=0, padx=2.5, pady=5, sticky="nwse")
        self.data_panal.grid(row=0, column=1, padx=2.5, pady=5, sticky="nwse")
    
    def run(self):

        self.mainloop()



app = App()
app.run()