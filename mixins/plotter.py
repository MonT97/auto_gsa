from matplotlib.axes import Axes

from typedefs import PlotInput, SamplePoints, AnalysisMethod, GraphType

from scipy import stats
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
        _method: AnalysisMethod = analysis_method
    
        def _plot_histo(ax: Axes, x: PlotInput,
                        y: PlotInput, color: str, kde_color: str) -> None:
            """
            Plots the Histogram.
            """
            _cat_x: list[str] = [str(i) for i in x] #? psedu categorical conversion

            ax.hist(x, weights=y, bins=len(x)-1,
                    color=color, density=True, label='histogram', **{'edgecolor': 'k'}) # type: ignore

            _ax_t: Axes = ax.twinx()#type: ignore
            _kde = stats.gaussian_kde(x, weights=y)
            _x_range = np.linspace(min(x), max(x), 50)
            _ax_t.plot(_x_range, _kde(_x_range), label='kde', color=kde_color)
            
            ax.set_xticks(x)
            ax.set_xticklabels(_cat_x)
            
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
                
                _padding: float = .35
                ax.set_xlim(x.min()-_padding, x.max()+_padding)
                ax.set_ylim(0-_padding*10, 100+_padding*10)
                _plot_cum(ax, x, y, points, clr, _method)