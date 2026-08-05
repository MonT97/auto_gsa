from tkinter import ttk
from typing import Final

# Constants:
# fonts
F_VIEWER_FONT: Final[tuple[str, int]] = ('Arial', 12)
TABLE_ROW_FONT: Final[tuple[str, int]] = ('Arial', 14)
TABLE_HDR_FONT: Final[tuple[str, int, str]] = ('Arial', 14, 'bold')

# color
GRAPH_COLOR_DEFAULT: Final[str] = '#1f7bb4'
TABLE_HDR_BG_ACTV_CLR: Final[str] = '#144870'
DATA_TABLE_HDR_BG_CLR: Final[str] = '#1f6aa5'
DATA_TABLE_ROW_BG_CLR: Final[str] = '#262626'
DATA_TABLE_FONT_CLR: Final[str] = '#ffffff'

# dimensions
ROW_HEIGHT: Final[int] = 25
HDR_PADDING: Final[tuple[int,int]] = (2,2)


class Styles():
    """
    A Singleton of sorts that applies styles.
    Currently two style present are:
    - Use apply_styles() to apply the styles.
    """
    def apply_styles(self) -> None:
        """
        A Singleton of sorts that applies styles.
        Currently two style present are:
        - F_Viewer.Treeview: for the [FileViewer].
        - DataTable.Treeview: for the [DataTable].
        """
        # FileViewer:
        _row_style = ttk.Style()
        _row_style.theme_use('default')
        _row_style.configure('F_Viewer.Treeview',
            foreground=DATA_TABLE_FONT_CLR,
            background=DATA_TABLE_ROW_BG_CLR,
            bordercolor=DATA_TABLE_HDR_BG_CLR,
            borderwidth=0,
            rowheight=ROW_HEIGHT,
            font=F_VIEWER_FONT,
            fieldbackground=DATA_TABLE_ROW_BG_CLR)
        _row_style.map('F_Viewer.Treeview')

        _header_style = ttk.Style()
        _header_style.configure('F_Viewer.Treeview.Heading', 
            relief='flat',
            foreground=DATA_TABLE_FONT_CLR,
            background=DATA_TABLE_HDR_BG_CLR,
            bordercolor=DATA_TABLE_HDR_BG_CLR,
            padding=HDR_PADDING,
            font=TABLE_HDR_FONT)
        _header_style.map('F_Viewer.Treeview.Heading',
            background=[('active', TABLE_HDR_BG_ACTV_CLR)])

        # DataTable:
        _d_style = ttk.Style()
        _d_style.theme_use('default')
        _d_style.configure('DataTable.Treeview',
            foreground=DATA_TABLE_FONT_CLR,
            background=DATA_TABLE_ROW_BG_CLR,
            bordercolor=DATA_TABLE_HDR_BG_CLR,
            borderwidth=0,
            rowheight=30,
            font=TABLE_ROW_FONT,
            fieldbackground=DATA_TABLE_ROW_BG_CLR)
        _d_style.map('DataTable.Treeview')

        _hdr_style = ttk.Style()
        _hdr_style.configure('DataTable.Treeview.Heading', 
            relief='flat',
            foreground=DATA_TABLE_FONT_CLR,
            background=DATA_TABLE_HDR_BG_CLR,
            bordercolor=DATA_TABLE_HDR_BG_CLR,
            padding=HDR_PADDING,
            font=TABLE_HDR_FONT)
        _hdr_style.map('DataTable.Treeview.Heading',
            background=[('active', TABLE_HDR_BG_ACTV_CLR)])