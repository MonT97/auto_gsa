from scipy.interpolate import PchipInterpolator, CubicSpline
from enums import GraphType

from matplotlib.axes import Axes
import pandas as pd
import numpy as np

class Analyzer():
    '''
        The class that wrangles the data, provides the stats and prepares it for plotting. 
    '''
    stats_list: list[dict[str,float]] = []
    def __init__(self, sample_data: pd.DataFrame, graph_type: GraphType):

        self.x = None
        self.y = None

        self.graph_type = graph_type

        self.points: list[tuple[float,float]] = []
        self._stats: dict[str, float] = {}

        self.trim_len: int = 0

        self.x, self.y = sample_data['phi'], sample_data['cum.wht%']

        self.interp_f = PchipInterpolator(self.x, self.y)

        match self.graph_type:

            case GraphType.CUM:
                
                self.y = np.linspace(0, 100, 1000, endpoint=False)
                self.x, self.trim_len = self.inverse(self.y, self.x.min())

                self.x = self.x[self.trim_len:]
                self.y = self.y[self.trim_len:]

            case GraphType.HIST:

                self.x = sample_data['phi']
                self.y = sample_data['wht%']

        self.calculate_stats()

    def inverse(self, wt_prcnts: np.ndarray, min_phi: float) -> tuple[np.ndarray, int]:

        temp_x: list = []
        trim_len: int = 0

        for wt_prcnt in wt_prcnts:
            phi = self.interp_f.solve(wt_prcnt)
            if len(phi) > 1:
                temp_x.append(phi[1]) # type: ignore
                if phi[1] < min_phi:
                    trim_len += 1
            else:
                temp_x.append(min_phi)
                trim_len += 1

        return (np.round(np.array(temp_x), 3), trim_len)

    def calculate_stats(self):

        self.wt_prcnts: list[int] = [5, 16, 25, 50, 75, 84, 95]
        self.xy_combo = zip(self.x, np.round(self.y, 3))# type: ignore
        
        self.points = [
                (wt_prcnt.item(), phi.item()) for phi, wt_prcnt in self.xy_combo if wt_prcnt in self.wt_prcnts
                ]
        
        valid: bool = True if len(self.points) == len(self.wt_prcnts) else False

        self.stats: dict[str, float] = {'mean': 0.0, 'std': 0.0, 'skewness': 0.0, 'kurtosis': 0.0}

        if valid:
            self.phi_prcnt: dict[str, float] = {f"{int(k)}": v for (k), v in self.points}

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
            
            self.stats = {
                'mean': self.mean, 'std': self.std,
                'skewness': self.skewness, 'kurtosis': self.kurtosis
                }

    def get_stats(self) -> dict[str, float]:

        self.stats = {k: round(v,2) for k, v in self.stats.items()}
        return self.stats

    def get_plot_data(self) -> list:
        '''
            [returns: x, y, points]
        '''
        return [self.x, self.y, self.points]


class Plotter():
    '''
        The class handeling the plotting of the data
    '''
    def __init__(self, x: pd.Series, y: pd.Series,
                 points: list[tuple[float,float]],
                 ax: Axes, _type: GraphType):

        self.x = x
        self.y = y
        self.points = points
        
        self.ax = ax

        self.type = _type

        match self.type:
            
            case GraphType.CUM:
                
                self.padding: float = .35
                self.ax.set_xlim(self.x.min()-self.padding, self.x.max()+self.padding)
                self.ax.set_ylim(0-self.padding*10, 100+self.padding*10)
                self.plot_cum()
            
            case GraphType.HIST:

                self.plot_histo()
    
    def plot_cum(self):

        for point in self.points:

            self.y_cord, self.x_cord = point
            self.x_cords: list = [self.ax.get_xlim()[0], self.x_cord, self.x_cord]
            self.y_cords: list = [self.y_cord, self.y_cord, self.ax.get_ylim()[0]]

            self.ax.plot(self.x_cords, self.y_cords, '--k', alpha=.25, zorder=2)
            self.ax.plot(self.x_cord, self.y_cord, '--.k', alpha=.25, zorder=1)
        
        self.ax.plot(self.x, self.y) #? this fixed the double plotting issue!
        self.ax.set_xlabel("phi (\u00D8)")
        self.ax.set_ylabel("cumulative weight %")
    
    def plot_histo(self):
        
        str_x: list[str] = [str(i) for i in self.x] #? psedu categorical conversion
        self.ax.hist(str_x, weights=self.y, bins=len(str_x), **{'edgecolor': 'k'}) # type: ignore

        self.ax.set_xlabel("phi (\u00D8)")
        self.ax.set_ylabel("weight %")