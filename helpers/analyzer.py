from typedefs import GraphType, SamplePoints, SampleStats, PlotInput, PlotData, StatsInterpretation
from scipy.interpolate import PchipInterpolator
from matplotlib.axes import Axes

import scipy.stats as stats
import pandas as pd
import numpy as np

class Analyzer():
    '''
    The class that wrangles the data, provides the stats, then prepares it for plotting. 
    '''
    stats_list: list[dict[str,float]] = []
    def __init__(self, sample_data: pd.DataFrame) -> None:
        
        self.sample_data = sample_data
        self.x, self.y, interp_f = self._get_input(sample_data)
        self.points, self.stats = self._calculate_stats(self.y.min(), interp_f)
        self.interpretation = self._interperate(self.stats)

    def _get_input(self,
                   sample_data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, PchipInterpolator]:
        '''
        Prepares the data [phi, cum.wt%] for stats calculation via interpolation using Scipy's PchipInterpolator, an implementation of Hermite plynomial interpolation.
        - -> (phi, cum.wt%)
        '''
        phi: pd.Series = sample_data['phi']
        cum_wht: pd.Series = sample_data['cum.wht%']

        def _inverse(
                interpolation_fn: PchipInterpolator,
                wt_prcnts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            '''
            Interpolation function inversion, get phi(x) at wt_prcnts(y).
            - -> tuple[phis, wt_prcnts]
            '''
            rounding_digits: int = 3
            phis_inversed: list[float] = []
            valid_wt_prcnts: list[float] = []

            for wt_prcnt in wt_prcnts:
                phi = interpolation_fn.solve(wt_prcnt)
                phis_inversed.append(phi[1])
                valid_wt_prcnts.append(wt_prcnt)
            
            x: np.ndarray = np.round(phis_inversed, rounding_digits)
            y: np.ndarray = np.round(valid_wt_prcnts, rounding_digits)

            return (x, y)
        
        interp_f = PchipInterpolator(phi, cum_wht)
        cap: float = cum_wht.max()
        step: float = cum_wht.min()
        y = np.linspace(step, cap, int(cap)*100, endpoint=False)
        
        return (*_inverse(interp_f, y), interp_f)

    def _calculate_stats(self,
            min_y: float, interp_f: PchipInterpolator
            ) -> tuple[SamplePoints, SampleStats]:
        '''
        Calculates stats: [mean, std, skewness, kurtosis], based on Folk&Ward 1957 graphical method if possible, otherwise, the Method of Moments is used.
        - min_y [cum.wht%].min()
        - interp_f [the interpolation function]
        '''
        wt_prcnts: list[float] = [5.0, 16.0, 25.0, 50.0, 75.0, 84.0, 95.0]
        
        points: SamplePoints = [
            (wt_prcnt, interp_f.solve(wt_prcnt)[1]) for wt_prcnt in wt_prcnts if wt_prcnt > min_y
            ]

        graphical_valid: bool = True if len(points) == len(wt_prcnts) else False
        
        #TODO: Turn this into a dataclass?!, No overkill
        stats: SampleStats = SampleStats()

        if graphical_valid:
            _get_phi: function = lambda phi: self.phi_prcnt[f'{phi}']
            self.phi_prcnt: dict[str, float] = {f"{int(k)}": v for (k), v in points}

            stats.mean = (_get_phi(16)+_get_phi(50)+_get_phi(84))/3
            stats.std = (((_get_phi(84)-_get_phi(16))/4)+((_get_phi(95)-_get_phi(5))/6.6))
            stats.skewness = (
                                ((_get_phi(16)+_get_phi(84)-(2*_get_phi(50)))/
                                (2*(_get_phi(84))-_get_phi(16)))+
                                (_get_phi(5)+_get_phi(95)-(2*_get_phi(50)))/
                                (2*(_get_phi(95))-_get_phi(5))
                                )
            stats.kurtosis = ((_get_phi(95)-_get_phi(5))/(2.44*(_get_phi(75)/_get_phi(25))))
        else:
            #TODO: I assume a 100g sample, universalize!
            sample_wht: float = 100.0 # to allow for measurement erro +- .1g

            phis = self.sample_data['phi']
            _get_midpoint: function = lambda i: (phis[i]+phis[i+1])/2
            d: np.ndarray = np.append([_get_midpoint(i) for i in range(len(phis)-1)], phis.max())
            f: np.ndarray = self.sample_data['wht%'].to_numpy()
            pan_fraction: float = sample_wht - f.sum()

            if pan_fraction < 5.0:
                N = f.sum() #? some say N=100, yet this is after ana_sed

                stats.mean = np.sum(f*d)/N
                stats.std = (np.sum(f*((d-stats.mean)**2))/N)**.5
                stats.skewness = np.sum(f*((d-stats.mean)**3))/(N*stats.std**3)
                stats.kurtosis = np.sum(f*((d-stats.mean)**4))/(N*stats.std**4)
            else:
                print(f'Pan fraction [{pan_fraction}] >5%, The analysis is unreliable, disregard this sample!.')
        
        return (points,stats)

    def _interperate(self, stats: SampleStats) -> StatsInterpretation:
        '''
        Interperate the sample stats according to [see the litrature]
        - std ------> sorting.
        - skewness -> the dominent tail, coarse/fine.
        - kurtosis ---> gives an idea about the distribution.
        '''
        def _sorting(std: float) -> str:

            sorting: str = ''

            if std < .35:
                sorting = 'very well'
            elif .35 <= std <= .5:
                sorting = 'well'
            elif .5 <= std <= .7:
                sorting = 'moderatrly well'
            elif .7 <= std <= 1:
                sorting = 'moderatrly'
            elif 1 <= std <= 2:
                sorting = 'poorly'
            elif 2 <= std <= 4:
                sorting = 'very poorly'
            else:
                sorting = 'extremely poorly'
            
            return sorting+' sorted'

        def _skew(skew: float) -> str:

            skewness: str = ''

            if skew > .3:
                skewness = 'strongy fine skewed'
            elif .3 >= skew >= .1:
                skewness = 'fine skewed'
            elif .1 >= skew >= -.1:
                skewness = 'near symmetrical'
            elif -.1 >= skew >= -.3:
                skewness = 'coarse skewed'
            else:
                skewness = 'strongly coarse skewed'
            
            return skewness       

        def _kurtosis(kurt: float) -> str:

            kurtosis: str = ''

            if kurt < .67:
                kurtosis = 'very platy'
            elif .67 <= kurt <= .9:
                kurtosis = 'platy'
            elif .9 <= kurt <= 1.11:
                kurtosis = 'meso'
            elif 1.11 <= kurt <= 1.5:
                kurtosis = 'lepto'
            elif 1.5 <= kurt <= 3:
                kurtosis = 'very lepto'
            else:
                kurtosis = 'extremely lepto'
            
            return kurtosis+'kurtic'

        interpretation: StatsInterpretation = StatsInterpretation()
        interpretation.sorting = _sorting(stats.std)
        interpretation.skewness = _skew(stats.skewness)
        interpretation.kurtosis = _kurtosis(stats.kurtosis)
        
        return interpretation

    def get_stats(self) -> SampleStats:
        '''
        Returns the stats.
        '''
        return self.stats

    def get_interpretation(self) -> StatsInterpretation:

        return self.interpretation

    def get_plot_data(self, graph_type: GraphType) -> PlotData:
        '''
        Returns the plot ready data.
        - -> [x, y], points]
        '''
        match graph_type:
            case GraphType.HIST:
                x: PlotInput = self.sample_data['phi']
                y: PlotInput = self.sample_data['wht%']
            case GraphType.CUM:
                x: PlotInput = self.x
                y: PlotInput = self.y

        return (x,y,self.points)


class Plotter():
    '''
    The class that handles the plotting of the data
    - clr ------> face color, hexadecimal.
    - line_clr -> kde color, hexadecimal.
    '''
    def __init__(self, x: PlotInput, y: PlotInput,
                 points: SamplePoints, ax: Axes, graph_type: GraphType,
                 clr: str = '#1f7bb4', kde_clr: str = 'k') -> None:
        
        match graph_type:

            case GraphType.HIST:
                self._plot_histo(ax, x, y, clr, kde_clr)

            case GraphType.CUM:
                
                padding: float = .35
                ax.set_xlim(x.min()-padding, x.max()+padding)
                ax.set_ylim(0-padding*10, 100+padding*10)
                self._plot_cum(ax, x, y, points, clr)
    
    def _plot_histo(self, ax: Axes, x: PlotInput, y: PlotInput, color: str, kde_color: str) -> None:
        '''
        Plots the Histogram.
        '''
        cat_x: list[str] = [str(i) for i in x] #? psedu categorical conversion

        ax.hist(x, weights=y, bins=len(x)-1,
                color=color, density=True, label='histogram', **{'edgecolor': 'k'}) # type: ignore

        ax_t: Axes = ax.twinx()#type: ignore
        kde = stats.gaussian_kde(x, weights=y)
        x_range = np.linspace(min(x), max(x), 50)
        ax_t.plot(x_range, kde(x_range), label='kde', color=kde_color)

        ax.set_xticks(x)
        ax.set_xticklabels(cat_x)
        
        ax.set_xlabel("phi (\u00D8)")
        ax.set_ylabel("weight %")

    def _plot_cum(self, ax: Axes, x: PlotInput, y: PlotInput,
                  points: SamplePoints, color: str) -> None:
        '''
        Plots the cumulative curve.
        '''
        for point in points:

            y_cord, x_cord = point
            x_cords: list = [ax.get_xlim()[0], x_cord, x_cord]
            y_cords: list = [y_cord, y_cord, ax.get_ylim()[0]]

            ax.plot(x_cords, y_cords, '--k', alpha=.25, zorder=2)
            ax.plot(x_cord, y_cord, '--.k', alpha=.25, zorder=1)
        
        ax.plot(x, y, color=color) #? this fixed the double plotting issue!
        ax.set_xlabel("phi (\u00D8)")
        ax.set_ylabel("cumulative weight %")