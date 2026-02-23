from platform import system
from widgets import MainPanal

import customtkinter as ctk


if system() != "Windows":
    print("Running in non-Windows OS, some eyecandy won't be visible!")


class App(ctk.CTk):

    def __init__(self, title:str="AutoGSA", size:tuple[int,int]=(800,500)) -> None:
        super().__init__()

        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        #TODO: append the main_panal and pack it!.
        self.main_panal: MainPanal = MainPanal(self)
        self.main_panal.pack(expand=1, fill='both')

    # TODO see if you can hide/handle the stuff chucked into the stdo
    def on_closing(self) -> None:

        self.quit()
        self.destroy()

    def run(self) -> None:

        self.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()