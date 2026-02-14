from scipy.interpolate import PchipInterpolator
from enums import GraphType
from matplotlib.axes import Axes
import pandas as pd
import numpy as np

type SamplePoints = list[tuple[float, float]]
type SampleStats = dict[str, float]
type PlotInput = pd.Series|np.ndarray
type PlotData = tuple[PlotInput, PlotInput, SamplePoints]

class Analyzer():
    '''
        The class that wrangles the data, provides the stats, then prepares it for plotting. 
    '''
    stats_list: list[dict[str,float]] = []
    def __init__(self, sample_data: pd.DataFrame):
        
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
                ) -> tuple[np.ndarray, int]:
            '''
                Interpolation function inversion, get phi(x) at wt_prcnts(y).
                - -> tuple[phis, trim_len]
            '''
            rounding_digits: int = 3
            phis_inversed: np.ndarray = np.zeros(shape=(len(wt_prcnts)))
            trim_len: int = 0

            for ind, wt_prcnt in enumerate(wt_prcnts):
                phi = interpolation_fn.solve(wt_prcnt)
                if len(phi) > 1:
                    phis_inversed[ind] = phi[1]
                    if phi[1] < min_phi:
                        trim_len += 1
                else:
                    phis_inversed[ind] = min_phi
                    trim_len += 1

            return (np.round(phis_inversed, rounding_digits), trim_len)
        
        interp_f = PchipInterpolator(phi, cum_wht) 
        y = np.linspace(0, 100, 1000, endpoint=False)
        x, trim_len = _inverse(interp_f, y, phi_min)

        x = x[trim_len:]
        y = y[trim_len:]
        
        return (x, y)

    def _calculate_stats(self,
            x: np.ndarray, y: np.ndarray
            ) -> tuple[SamplePoints, SampleStats]:
        '''
            Calculates stats: [mean, std, skewness, kurtosis], based on Folk&Ward 1957 graphical method if possible, otherwise, the Method of Moments is used.
            - x [wht%]. y [cum.wht%]
        '''
        wt_prcnts: list[int] = [5, 16, 25, 50, 75, 84, 95]
        xy_combo = zip(x, np.round(y, 3))# type: ignore
        
        points: SamplePoints = [
                (wt_prcnt.item(), phi.item()) for phi, wt_prcnt in xy_combo if wt_prcnt in wt_prcnts
                ]
        
        graphical_valid: bool = True if len(points) == len(wt_prcnts) else False

        stats: SampleStats = {'mean': 0.0, 'std': 0.0, 'skewness': 0.0, 'kurtosis': 0.0}

        if graphical_valid:
            self.phi_prcnt: dict[str, float] = {f"{int(k)}": v for (k), v in points}

            self.mean: float = (self.phi_prcnt['16']+self.phi_prcnt['50']+self.phi_prcnt['84'])/3
            self.std: float = (
                                ((self.phi_prcnt['84']-self.phi_prcnt['16'])/4)+
                                ((self.phi_prcnt['95']-self.phi_prcnt['5'])/6.6)
                                )
            self.skewness: float = (
                                    ((self.phi_prcnt['16']+self.phi_prcnt['84']-(2*self.phi_prcnt['50']))/
                                    (2*(self.phi_prcnt['84'])-self.phi_prcnt['16']))+
                                    (self.phi_prcnt['5']+self.phi_prcnt['95']-(2*self.phi_prcnt['50']))/
                                    (2*(self.phi_prcnt['95'])-self.phi_prcnt['5'])
                                    )
            self.kurtosis: float = (
                                    (self.phi_prcnt['95']-self.phi_prcnt['5'])/
                                    2.44*(self.phi_prcnt['75']/self.phi_prcnt['25'])
                                    )
        else:
            phi: np.ndarray = np.array(self.sample_data['phi'])
            f: np.ndarray = np.array(self.sample_data['wht%'])
            f = np.append(f[:-2], f[-2:].sum()) #! as f is the median wt value, this is a temp fix
            d: np.ndarray = np.array((phi[:-1]+phi[1:])/2)

            N = f.sum() #? some say N=100, yet this is after ana_sed

            self.mean = (np.sum(f*d))/N
            self.std = ((np.sum(f*((d-self.mean)**2)))/N)**.5
            self.skewness = ((np.sum(f*((d-self.mean)**3)))/(N*self.std**3))
            self.kurtosis = ((np.sum(f*((d-self.mean)**4)))/(N*self.std**4))
    
        stats = {
            'mean': self.mean, 'std': self.std,
            'skewness': self.skewness, 'kurtosis': self.kurtosis
            }
        
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
                 ax: Axes, _type: GraphType):
        
        match _type:

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