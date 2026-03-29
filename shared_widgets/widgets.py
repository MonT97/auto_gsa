from collections.abc import Callable

import customtkinter as ctk

class ColorPicker(ctk.CTkFrame):
    '''
    CTkFrame:
        An (RGB) color picker.
    Note: all masters should have a on_preview_press(color) function.
    '''
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master)

        self.columnconfigure(0, weight=1, uniform='b')
        self.columnconfigure(1, weight=2, uniform='b')
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')
        self.rowconfigure(2, weight=1, uniform='b')

        self.color: str = '#000000'

        self.preview: ctk.CTkButton = ctk.CTkButton(self,
                text='set', border_color='red', border_width=2,
                command= lambda: self._update_color(master, self.color))

        _r: ctk.IntVar = ctk.IntVar(self, value=138)
        _g: ctk.IntVar = ctk.IntVar(self, value=117)
        _b: ctk.IntVar = ctk.IntVar(self, value=216)

        self._set_color((_r,_g,_b))

        _r_slider: ColorSlider = ColorSlider(self, 'r', _r, lambda _: self._set_color((_r,_g,_b)))
        _g_slider: ColorSlider = ColorSlider(self, 'g', _g, lambda _: self._set_color((_r,_g,_b)))
        _b_slider: ColorSlider = ColorSlider(self, 'b', _b, lambda _: self._set_color((_r,_g,_b)))
    
        self.preview.grid(column=0, row=0, rowspan=3, padx=5, pady=2, sticky='nsew')
        _r_slider.grid(column=1, row=0, rowspan=1, padx=5)
        _g_slider.grid(column=1, row=1, rowspan=1, padx=5)
        _b_slider.grid(column=1, row=2, rowspan=1, padx=5)

    def _set_color(self, rgb: tuple[ctk.IntVar,ctk.IntVar,ctk.IntVar]) -> None:
        '''
        Sets the color.
        '''
        clr: tuple[int,int,int] = tuple(i.get() for i in rgb)#type: ignore
        crnt_hvr_clr: list[str] = self.preview.cget('hover_color')
        
        self.color = '#'+''.join([f'{c:02x}' for c in clr])
        self.preview.configure(fg_color = self.color)

        if sum(clr) > 245:
            self.preview.configure(text_color = '#000000')
            self.preview.configure(hover_color=[crnt_hvr_clr[0],'#ffffff'])
        if sum(clr) < 245:
            self.preview.configure(text_color = '#ffffff')
            self.preview.configure(hover_color=[crnt_hvr_clr[0],'#000000'])

        if self.preview.cget('border_color') != 'red':
            self.preview.configure(border_color='red', text='set')

    def _update_color(self, master: ctk.CTkFrame, color: str) -> None:
        '''
        Update the graph with the new color, delegated to master.
        '''
        master.on_preview_press(color) #type: ignore
        self.preview.configure(border_color='green', text='set!')


class ColorSlider(ctk.CTkSlider):
    '''
    CTkSlider:
        For picking the color bandwise.
        - clr_band [str]:what band of the (R,G,B) band the slider represents.
        - variable [ctk.IntVar]:value to be adjusted through the slider.
        - command [Callable]:the behaviour to be linked with.
    '''
    def __init__(self,
                 master: ColorPicker, clr_band: str, variable: ctk.IntVar,
                 command: Callable) -> None:
        super().__init__(master)
        clrs: tuple[str, str, str] = ('','','')

        match clr_band:
            case 'r':
                clrs = ('#b50000', '#ff0000', '#855656')
            case 'g':
                clrs = ('#00b500', '#00ff00', '#568556')
            case 'b':
                clrs = ('#0000b5', '#0000ff', '#565685')

        self.configure(variable=variable, height=13,
            button_color=clrs[0], button_hover_color=clrs[1], progress_color=clrs[2],
            button_corner_radius=5, border_width=5, button_length=18,
            from_=0, to=255, number_of_steps=255, command=command)