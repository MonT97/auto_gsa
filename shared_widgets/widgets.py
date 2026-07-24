from collections.abc import Callable

import customtkinter as ctk
from PIL import Image

# Constants
# icon:
ICON_SIZE = (34,34)

PREVIEW_ICON_ON_BK = Image.open('assets/check_box_on_bk.png')
PREVIEW_ICON_ON_WH = Image.open('assets/check_box_on_wh.png')
PREVIEW_ICON_OFF_BK = Image.open('assets/check_box_off_bk.png')
PREVIEW_ICON_OFF_WH = Image.open('assets/check_box_off_wh.png')

# color:
HOVER_CONTRAST = 35 # the contrast from the currnet color
assert HOVER_CONTRAST < 127, f'{HOVER_CONTRAST} should never exceed 127 for the math to checkout!'
TONE_THRESHOLD = 127

DEFAULT_COLOR = '#1f7bb4'
HOVER_COLOR = '#ffffff'
BORDER_COLOR_ACTIVE = '#00ff00'
BORDER_COLOR_INACTIVE = '#ff0000'
DEFAULT_R_COLOR = ('#b50000', '#ff0000', '#855656')
DEFAULT_G_COLOR = ('#00b500', '#00ff00', '#568556')
DEFAULT_B_COLOR = ('#0000b5', '#0000ff', '#565685')


class ColorPicker(ctk.CTkFrame):
    """
    CTkFrame:
        An (RGB) color picker.
    Note: all masters should have on_preview_press(color) function, assertion enforced.
    """
    def __init__(self, master: ctk.CTkFrame) -> None:
        """
        An (RGB) color picker.
        Note: all masters should have on_preview_press(color) function, assertion enforced.
        """
        super().__init__(master)

        assert getattr(master, 'on_preview_press')

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=2, uniform='a')
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')
        self.rowconfigure(2, weight=1, uniform='b')

        self.color: str = DEFAULT_COLOR
        self.default_rgb: tuple = self._convert_clr(self.color) #type: ignore

        self.preview: ctk.CTkButton = ctk.CTkButton(self,
                text='', border_color='red', border_width=2,
                image=ctk.CTkImage(PREVIEW_ICON_OFF_WH,size=ICON_SIZE),
                command= lambda: self._update_color(master, self.color))

        self.r: ctk.IntVar = ctk.IntVar(self, value=self.default_rgb[0])
        self.g: ctk.IntVar = ctk.IntVar(self, value=self.default_rgb[1])
        self.b: ctk.IntVar = ctk.IntVar(self, value=self.default_rgb[2])

        self._set_color((self.r,self.g,self.b))

        _r_slider = ColorSlider(self, 'r', self.r,
                    lambda _: self._set_color((self.r,self.g,self.b)))
        _g_slider = ColorSlider(self, 'g', self.g,
                    lambda _: self._set_color((self.r,self.g,self.b)))
        _b_slider = ColorSlider(self, 'b', self.b,
                    lambda _: self._set_color((self.r,self.g,self.b)))
    
        self.preview.grid(column=0, row=0, rowspan=3, padx=5, pady=5, sticky='nsew')
        _r_slider.grid(column=1, row=0, rowspan=1, padx=5)
        _g_slider.grid(column=1, row=1, rowspan=1, padx=5)
        _b_slider.grid(column=1, row=2, rowspan=1, padx=5)

    def update_clr_and_intvars(self, color: str) -> None:
        _color: tuple = self._convert_clr(color) #type: ignore
        
        self.r.set(_color[0])
        self.g.set(_color[1])
        self.b.set(_color[2])
        
        self._set_color((self.r,self.g,self.b))


    def _convert_clr(self, color: str|tuple[int,int,int]) -> str|tuple:
        """
        Converts the given [color] into the opposite format, a [color:str] returns a [color:tuple] and vise versa.
        - color: the color in either str or tuple form.
        """
        if isinstance(color, str):
            color = color.lstrip('#')
            _clr = tuple(int(f'{color[i]}{color[i+1]}',16) for i in range(0,len(color),2))
        elif isinstance(color, tuple):
            _clr = '#'+''.join([f'{c:02x}' for c in color])
        return _clr

    def _set_color(self, rgb: tuple[ctk.IntVar,ctk.IntVar,ctk.IntVar]) -> None:
        """
        Sets the color.
        """
        _clr: tuple[int,int,int] = tuple(i.get() for i in rgb) #type: ignore
        
        def get_hvr(clr: tuple) -> str:
            """
            Computes the hover color based on max(_clr).
            """
            _cap: int = 255-HOVER_CONTRAST
            # the next 2 lines calculates the contrast weighted by thier rank!
            _get_wt = lambda x: int(HOVER_CONTRAST-(HOVER_CONTRAST*((x+1)/10)))
            _get_val = lambda c, id_: c+_get_wt(id_) if c < _cap else c-_get_wt(id_)
            _ranked_clr = {k: v for v, k in enumerate(sorted(clr,reverse=True))}
            _rank = [_ranked_clr[c] for c in clr]
            _hvr_clr = tuple(_get_val(c,rank) for c,rank in zip(clr, _rank))

            return self._convert_clr(_hvr_clr) #type:ignore

        self.color = self._convert_clr(_clr) #type:ignore
        self.preview.configure(fg_color = self.color)
        _hover_color = get_hvr(_clr)

        if max(_clr) > TONE_THRESHOLD:
            _image = ctk.CTkImage(PREVIEW_ICON_OFF_BK, size=ICON_SIZE)
        else:
            _image = ctk.CTkImage(PREVIEW_ICON_OFF_WH, size=ICON_SIZE)

        self.preview.configure(hover_color=_hover_color,image=_image)

        if self.preview.cget('border_color') != BORDER_COLOR_INACTIVE:
            self.preview.configure(border_color=BORDER_COLOR_INACTIVE)

    def _update_color(self, master: ctk.CTkFrame, color: str) -> None:
        """
        Update the graph with the new color, delegated to master.
        """
        master.on_preview_press(color) #type: ignore
        _max: int = max(self._convert_clr(color)) #type: ignore

        _img = PREVIEW_ICON_ON_BK if _max > TONE_THRESHOLD else PREVIEW_ICON_ON_WH

        self.preview.configure(
            border_color=BORDER_COLOR_ACTIVE,
            image=ctk.CTkImage(_img, size=ICON_SIZE))


class ColorSlider(ctk.CTkSlider):
    """
    CTkSlider:
        For picking the color bandwise.
        - clr_band [str]:what band of the (R,G,B) band the slider represents.
        - variable [ctk.IntVar]:value to be adjusted through the slider.
        - command [Callable]:the behavior to be linked with.
    """
    def __init__(self,
                 master: ColorPicker, clr_band: str, variable: ctk.IntVar,
                 command: Callable) -> None:
        """
        For picking the color bandwise.
        - clr_band [str]:what band of the (R,G,B) band the slider represents.
        - variable [ctk.IntVar]:value to be adjusted through the slider.
        - command [Callable]:the behavior to be linked with.
        """
        super().__init__(master)
        clrs: tuple[str, str, str] = ('','','')

        match clr_band:
            case 'r':
                clrs = DEFAULT_R_COLOR
            case 'g':
                clrs = DEFAULT_G_COLOR
            case 'b':
                clrs = DEFAULT_B_COLOR

        self.configure(variable=variable, height=13,
            button_color=clrs[0], button_hover_color=clrs[1], progress_color=clrs[2],
            button_corner_radius=5, border_width=5, button_length=18,
            from_=0, to=255, number_of_steps=255, command=command)