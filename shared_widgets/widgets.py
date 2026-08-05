from collections.abc import Callable
from typing import Final, overload

import customtkinter as ctk
from PIL import Image

from mixins import Observer, HasToolTip
from typedefs import Signal

# Constants:
# icon
ICON_SIZE: Final[tuple[int,int]] = (34,34)

PREVIEW_ICON_ON_BK: Final = Image.open('assets/check_box_on_bk.png')
PREVIEW_ICON_ON_WH: Final = Image.open('assets/check_box_on_wh.png')
PREVIEW_ICON_OFF_BK: Final = Image.open('assets/check_box_off_bk.png')
PREVIEW_ICON_OFF_WH: Final = Image.open('assets/check_box_off_wh.png')

# color
TONE_THRESHOLD: Final[int] = 127
HOVER_CONTRAST: Final[int] = 35 # the contrast from the current color
assert HOVER_CONTRAST < 127, f'{HOVER_CONTRAST} should never exceed 127 for the math to checkout!'
DEFAULT_COLOR: Final[str] = '#1f7bb4'
HOVER_COLOR: Final[str] = '#ffffff'
BORDER_COLOR_ACTIVE: Final[str] = '#00ff00'
BORDER_COLOR_INACTIVE: Final[str] = '#ff0000'
DEFAULT_R_COLOR: Final[tuple[str,str,str]] = ('#b50000', '#ff0000', '#855656')
DEFAULT_G_COLOR: Final[tuple[str,str,str]] = ('#00b500', '#00ff00', '#568556')
DEFAULT_B_COLOR: Final[tuple[str,str,str]] = ('#0000b5', '#0000ff', '#565685')


class ColorPicker(ctk.CTkFrame, Observer, HasToolTip):
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

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=2, uniform='a')
        self.rowconfigure(0, weight=1, uniform='b')
        self.rowconfigure(1, weight=1, uniform='b')
        self.rowconfigure(2, weight=1, uniform='b')

        self._color: str = DEFAULT_COLOR
        self._default_rgb: tuple = self._convert_clr(self._color) #type: ignore

        self._preview: ctk.CTkButton = ctk.CTkButton(self,
                text='', border_color='red', border_width=2,
                image=ctk.CTkImage(PREVIEW_ICON_OFF_WH,size=ICON_SIZE),
                command= lambda: self._on_preview_btn_press(self._color))

        self._preview.bind('<Button-3>', lambda _: self.update_clr_and_intvars(DEFAULT_COLOR))

        self.htt_tip(self._preview, '[lift click]: to set the color\n[right click]: to reset to default')

        self._r: ctk.IntVar = ctk.IntVar(self, value=self._default_rgb[0])
        self._g: ctk.IntVar = ctk.IntVar(self, value=self._default_rgb[1])
        self._b: ctk.IntVar = ctk.IntVar(self, value=self._default_rgb[2])

        self._set_color((self._r,self._g,self._b))

        _r_slider = ColorSlider(self, 'r', self._r,
                    lambda _: self._set_color((self._r,self._g,self._b)))
        _g_slider = ColorSlider(self, 'g', self._g,
                    lambda _: self._set_color((self._r,self._g,self._b)))
        _b_slider = ColorSlider(self, 'b', self._b,
                    lambda _: self._set_color((self._r,self._g,self._b)))
    
        self._preview.grid(column=0, row=0, rowspan=3, padx=5, pady=5, sticky='nsew')
        _r_slider.grid(column=1, row=0, rowspan=1, padx=5, pady=(5,0))
        _g_slider.grid(column=1, row=1, rowspan=1, padx=5, pady=0)
        _b_slider.grid(column=1, row=2, rowspan=1, padx=5, pady=(0,5))

    def update_clr_and_intvars(self, color: str) -> None:
        _color: tuple = self._convert_clr(color) #type: ignore
        
        self._r.set(_color[0])
        self._g.set(_color[1])
        self._b.set(_color[2])
        
        self._set_color((self._r,self._g,self._b))
        self._on_preview_btn_press(color)

    @overload
    def _convert_clr(self, color: str) -> tuple[int,int,int]: ...
    @overload
    def _convert_clr(self, color: tuple[int,int,int]) -> str: ...
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

        self._color = self._convert_clr(_clr) #type:ignore
        self._preview.configure(fg_color = self._color)
        _hover_color = get_hvr(_clr)

        if max(_clr) > TONE_THRESHOLD:
            _image = ctk.CTkImage(PREVIEW_ICON_OFF_BK, size=ICON_SIZE)
        else:
            _image = ctk.CTkImage(PREVIEW_ICON_OFF_WH, size=ICON_SIZE)

        self._preview.configure(hover_color=_hover_color,image=_image)

        if self._preview.cget('border_color') != BORDER_COLOR_INACTIVE:
            self._preview.configure(border_color=BORDER_COLOR_INACTIVE)

    def _on_preview_btn_press(self, color: str) -> None:
        """
        Picks the color and broadcasts [Signal.COLOR].
        """
        _max: int = max(self._convert_clr(color))

        _img = PREVIEW_ICON_ON_BK if _max > TONE_THRESHOLD else PREVIEW_ICON_ON_WH

        self._preview.configure(
            border_color=BORDER_COLOR_ACTIVE,
            image=ctk.CTkImage(_img, size=ICON_SIZE))
        
        self.obs_broadcast(Signal.COLOR, self, (color,))


class ColorSlider(ctk.CTkSlider):
    """
    CTkSlider:
        For picking the color bandwise.
    """
    def __init__(self,
                 master: ColorPicker, clr_band: str, variable: ctk.IntVar,
                 command: Callable) -> None:
        """
        For picking the color bandwise.
        - clr_band: what band of the (R,G,B) band the slider represents.
        - variable: value to be adjusted through the slider.
        - command: the behavior to be linked with.
        """
        super().__init__(master)
        _clrs: tuple[str, str, str] = ('','','')

        match clr_band:
            case 'r':
                _clrs = DEFAULT_R_COLOR
            case 'g':
                _clrs = DEFAULT_G_COLOR
            case 'b':
                _clrs = DEFAULT_B_COLOR

        self.configure(variable=variable, height=15,
            button_color=_clrs[0], button_hover_color=_clrs[1], progress_color=_clrs[2],
            button_corner_radius=5, border_width=4, button_length=18,
            from_=0, to=255, number_of_steps=255, command=command)