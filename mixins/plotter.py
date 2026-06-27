from matplotlib.axes import Axes

from typedefs import PlotInput, SamplePoints, AnalysisMethod, GraphType

import numpy as np

class CanPlot():
    """
    Gives the ability to plot data.
    """
    def cp_plot (self, x: PlotInput, y: PlotInput,
                 points: SamplePoints, ax: Axes, graph_type: GraphType,
                 analysis_method: AnalysisMethod, clr: str = '#1f7bb4',
                 kde_clr: str = 'k') -> None:
        """
        The plotting functoin:
            - clr ------> face color, hexadecimal.
            - line_clr -> kde color, hexadecimal.
        """
        def _plot_histo(ax: Axes, x: PlotInput,
                        y: PlotInput, color: str, kde_color: str) -> None:
            """
            Plots the Histogram.
            """
            _interval_x: float = x.diff().mode()[0] #type: ignore
            _edges: np.ndarray = np.concatenate([x[:1]-_interval_x, x])

            ax.stairs(values=y, edges=_edges, fill=True,
                      color=color, zorder=2,
                      **{'linewidth': 1.5, 'edgecolor': 'k'})
            ax.grid(True, axis='y', zorder=1)

            #plot vertical lines to make pseudo bins!:
            for x,y in zip(x[:-1],y[:-1]):
                ax.plot((x,x), (0,y), '-k' )#type: ignore

            ax.set_xticks(_edges)
            ax.set_xticklabels(_edges)

            ax.set_xlabel("phi (\u00D8)")
            ax.set_ylabel("weight %")

        def _plot_cum(ax: Axes, x: PlotInput, y: PlotInput, points: SamplePoints,
                      color: str, analysis_method: AnalysisMethod) -> None:
            """
            Plots the cumulative curve.
            """
            if analysis_method == AnalysisMethod.GRAPHICAL:
                for _point in points:

                    _y_cord, _x_cord = _point
                    _x_cords: list = [ax.get_xlim()[0], _x_cord, _x_cord]
                    _y_cords: list = [_y_cord, _y_cord, ax.get_ylim()[0]]

                    ax.plot(_x_cords, _y_cords, '--k', alpha=.25, zorder=2)
                    ax.plot(_x_cord, _y_cord, '--.k', alpha=.25, zorder=1)
            
            ax.plot(x, y, color=color) #? this fixed the double plotting issue!
            ax.set_xlabel("phi (\u00D8)")
            ax.set_ylabel("cumulative weight %")
    
        match graph_type:
            case GraphType.HIST:
                _plot_histo(ax, x, y, clr, kde_clr)

            case GraphType.CUM:       
                if analysis_method != AnalysisMethod.TWOPOINTS:
                    _padding: float = .35
                    ax.set_xlim(x.min()-_padding/5, x.max()+_padding/5)
                    ax.set_ylim(0-_padding*10, 100+_padding*10)
                    _plot_cum(ax, x, y, points, clr, analysis_method)