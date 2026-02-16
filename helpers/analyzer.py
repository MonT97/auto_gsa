from typedefs import GraphType, SamplePoints, SampleStats, PlotInput, PlotData
from scipy.interpolate import PchipInterpolator
from matplotlib.axes import Axes

import pandas as pd
import numpy as np

class Analyzer():
    '''
        The class that wrangles the data, provides the stats, then prepares it for plotting. 
    '''
    stats_list: list[dict[str,float]] = []
    def __init__(self, sample_data: pd.DataFrame) -> None:
        
        self.sample_data = sample_data
        self.x, self.y = self._set_xy(sample_data)
        self.points, self.stats = self._calculate_stats(self.x, self.y)

    def _set_xy(self, sample_data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        '''
            Prepares the data [phi, cum.wt%] for stats calculation via interpolation using Scipy's PchipInterpolator, an implementation of Hermite plynomial interpolation.
            - -> (phi, cum.wt%)
        '''
        phi: pd.Series = sample_data['phi']
        phi_min: float = phi.min()
        cum_wht: pd.Series = sample_data['cum.wht%']

        def _inverse(
                interpolation_fn: PchipInterpolator,
                wt_prcnts: np.ndarray, min_phi: float
                ) -> tuple[np.ndarray, np.ndarray]:
            '''
                Interpolation function inversion, get phi(x) at wt_prcnts(y).
                - -> tuple[phis, wt_prcnts]
            '''
            rounding_digits: int = 3
            phis_inversed: list[float] = []
            valid_wt_prcnts: list[float] = []

            for wt_prcnt in wt_prcnts:
                phi = interpolation_fn.solve(wt_prcnt)
                if (len(phi) > 1) and (phi[1] >= min_phi):
                    phis_inversed.append(phi[1])
                    valid_wt_prcnts.append(wt_prcnt)
            
            x: np.ndarray = np.round(phis_inversed, rounding_digits)
            y: np.ndarray = np.round(valid_wt_prcnts, rounding_digits)

            return (x, y)
        
        interp_f = PchipInterpolator(phi, cum_wht) 
        y = np.linspace(0, cum_wht.max(), int(cum_wht.max()*100), endpoint=False)
        
        return (_inverse(interp_f, y, phi_min))

    def _calculate_stats(self,
            x: np.ndarray, y: np.ndarray
            ) -> tuple[SamplePoints, SampleStats]:
        '''
            Calculates stats: [mean, std, skewness, kurtosis], based on Folk&Ward 1957 graphical method if possible, otherwise, the Method of Moments is used.
            - x [phi]
            - y [cum.wht%]
        '''
        wt_prcnts: list[int] = [5, 16, 25, 50, 75, 84, 95]
        xy_combo = zip(x, np.round(y, 3))
        
        points: SamplePoints = [
                (wt_prcnt.item(), phi.item()) for phi, wt_prcnt in xy_combo if wt_prcnt in wt_prcnts
                ]
        
        graphical_valid: bool = True if len(points) == len(wt_prcnts) else False

        #TODO: Turn this into a dataclass?!
        stats: SampleStats = {'mean': 0.0, 'std': 0.0, 'skewness': 0.0, 'kurtosis': 0.0}

        if graphical_valid:
            self.phi_prcnt: dict[str, float] = {f"{int(k)}": v for (k), v in points}

            stats['mean'] = (self.phi_prcnt['16']+self.phi_prcnt['50']+self.phi_prcnt['84'])/3
            stats['std'] = (
                            ((self.phi_prcnt['84']-self.phi_prcnt['16'])/4)+
                            ((self.phi_prcnt['95']-self.phi_prcnt['5'])/6.6)
                                )
            stats['skewness'] = (
                                ((self.phi_prcnt['16']+self.phi_prcnt['84']-(2*self.phi_prcnt['50']))/
                                (2*(self.phi_prcnt['84'])-self.phi_prcnt['16']))+
                                (self.phi_prcnt['5']+self.phi_prcnt['95']-(2*self.phi_prcnt['50']))/
                                (2*(self.phi_prcnt['95'])-self.phi_prcnt['5'])
                                )
            stats['kurtosis'] = (
                                (self.phi_prcnt['95']-self.phi_prcnt['5'])/
                                2.44*(self.phi_prcnt['75']/self.phi_prcnt['25'])
                                )
        else:
            #TODO: I assume a 100g sample, universalize!
            sample_wht: float = 100.0 # to allow for measurement erro +- .1g

            phis = self.sample_data['phi']
            d: np.ndarray = np.append(
                [(phis[i]+phis[i+1])/2 for i in range(len(phis)-1)], phis.max())
            f: np.ndarray = np.array(self.sample_data['wht%'])
            pan_fraction: float = sample_wht - f.sum()
            print(f'{d=}\n{f=}')

            if pan_fraction < 5.0:
                N = f.sum() #? some say N=100, yet this is after ana_sed

                stats['mean'] = (np.sum(f*d))/N
                stats['std'] = ((np.sum(f*((d-stats['mean'])**2)))/N)**.5
                stats['skewness'] = ((np.sum(f*((d-stats['mean'])**3)))/(N*stats['std']**3))
                stats['kurtosis'] = ((np.sum(f*((d-stats['mean'])**4)))/(N*stats['std']**4))
            else:
                print(f'{pan_fraction=} > 5%, The analysis is unreliable, disregard this sample!.')
        
        return (points,stats)

    def get_stats(self) -> SampleStats:
        '''
            Returns the stats.
        '''
        self.stats = {k: round(v,2) for k, v in self.stats.items()}
        return self.stats

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
    '''
    def __init__(self, x: PlotInput, y: PlotInput,
                 points: SamplePoints,
                 ax: Axes, graph_type: GraphType) -> None:
        
        match graph_type:

            case GraphType.HIST:
                self._plot_histo(ax, x, y)

            case GraphType.CUM:
                
                padding: float = .35
                ax.set_xlim(x.min()-padding, x.max()+padding)
                ax.set_ylim(0-padding*10, 100+padding*10)
                self._plot_cum(ax, x, y, points)
    
    def _plot_histo(self, ax: Axes, x: PlotInput, y: PlotInput) -> None:
        '''
            Plots the Histogram.
        '''
        cat_x: list[str] = [str(i) for i in x] #? psedu categorical conversion

        ax.hist(cat_x, weights=y, bins=len(cat_x), **{'edgecolor': 'k'}) # type: ignore

        ax.set_xlabel("phi (\u00D8)")
        ax.set_ylabel("weight %")

    def _plot_cum(self, ax: Axes, x: PlotInput, y: PlotInput, points: SamplePoints) -> None:
        '''
            Plots the cumulative curve.
        '''
        for point in points:

            y_cord, x_cord = point
            x_cords: list = [ax.get_xlim()[0], x_cord, x_cord]
            y_cords: list = [y_cord, y_cord, ax.get_ylim()[0]]

            ax.plot(x_cords, y_cords, '--k', alpha=.25, zorder=2)
            ax.plot(x_cord, y_cord, '--.k', alpha=.25, zorder=1)
        
        ax.plot(x, y) #? this fixed the double plotting issue!
        ax.set_xlabel("phi (\u00D8)")
        ax.set_ylabel("cumulative weight %") 