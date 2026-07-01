from mixins import HasToolTip
from utils import utils

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

        utils.bg_transparent([self.approve_btn, self.cancel_btn])

        self.cancel_btn.place(anchor='w', relx=0, rely=.5, relwidth=.2, relheight=1)
        self.approve_btn.place(anchor='e', relx=1, rely=.5, relwidth=.2, relheight=1)
        
        self.main_frame.pack(side='top', expand=True, fill='both', padx=5, pady=(5,0))
        self.button_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        self.after(200, lambda: self.iconbitmap('assets/default.ico'))

    def close(self) -> None:
        """
        Closes the window.
        """
        self.destroy()