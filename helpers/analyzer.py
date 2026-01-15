from scipy.interpolate import CubicSpline
from enums import GraphType

from matplotlib.axes import Axes
import pandas as pd
import numpy as np

class Analyzer():
    '''
        The class that wrangles the data and then provides the stats and make the said data plot ready. 
    '''
    stats_list: list[dict[str,float]] = []
    def __init__(self, sample_data: pd.DataFrame, graph_type: GraphType):

        self.x = None
        self.y = None

        self.points: list[tuple[float,float]] = []
        self._stats: dict[str, float] = {}

        match graph_type:

            case GraphType.CUM:

                x, y = sample_data['phi'], sample_data['cum.wht%']

                self.interp = CubicSpline(x, y)
                self.x = np.linspace(x.min(), x.max(), 500)
                self.y = self.interp(self.x)

            case GraphType.HIST:

                self.x = sample_data['phi']
                self.y = sample_data['wht%']

        self.calculate_stats(sample_data['phi'], sample_data['cum.wht%'])

    def calculate_stats(self, x: pd.Series, y: pd.Series):

        self.phi_perc: list[int] = [5, 16, 25, 50, 75, 84, 95]
        self.points = [
                (round(np.interp(phi,y,x), 2), phi) for phi in self.phi_perc# type: ignore
                ]
        self.phi_quant: dict[str, float] = {f"{k}": v for v, k in self.points}
        
        self.mean: float = (self.phi_quant['16']+self.phi_quant['50']+self.phi_quant['84'])/3
        self.std: float = (
                            ((self.phi_quant['84']-self.phi_quant['16'])/4)+
                            ((self.phi_quant['95']-self.phi_quant['5'])/6.6)
                            )
        self.skewness: float = (
                                ((self.phi_quant['16']+self.phi_quant['84']-(2*self.phi_quant['50']))/
                                (2*(self.phi_quant['84'])-self.phi_quant['16']))+
                                (self.phi_quant['5']+self.phi_quant['95']-(2*self.phi_quant['50']))/
                                (2*(self.phi_quant['95'])-self.phi_quant['5'])
                                )
        self.kurtosis: float = (
                                (self.phi_quant['95']-self.phi_quant['5'])/
                                2.44*(self.phi_quant['75']/self.phi_quant['25'])
                                )
        self.stats = {'mean': self.mean, 'std': self.std,
                            'skewness': self.skewness, 'kurtosis': self.kurtosis}

    def get_stats(self) -> dict[str, float]:

        self.stats = {k: round(v,2) for k, v in self.stats.items()}
        return self.stats

    def get_plot_data(self) -> list:
        '''
            [returns: x, y, points]
        '''
        return[self.x, self.y, self.points]


class Plotter():
    '''
        The class handeling the plotting of the data both in terms of going and showing!
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
                
                self.ax.set_xlim(-3, 5)
                self.ax.set_ylim(0, 100)
                self.plot_cum()
            
            case GraphType.HIST:

                self.plot_histo()
    
    def plot_cum(self):
        
        for point in self.points:

            self.x_cord, self.y_cord = point
            self.x_cords: list = [self.ax.get_xlim()[0], self.x_cord, self.x_cord]
            self.y_cords: list = [self.y_cord, self.y_cord, self.ax.get_ylim()[0]]

            self.ax.plot(self.x, self.y)
            self.ax.plot(self.x_cords, self.y_cords, '--k')
            self.ax.plot(self.x_cord, self.y_cord, '--.k')
            self.ax.annotate(f"x={round(self.x_cord,2)}, y={self.y_cord}%",
                            xy=(0.2, self.y_cord))
        
        self.ax.set_xlabel("phi (\u00D8)")
        self.ax.set_ylabel("cumulative weight %")
    
    def plot_histo(self):

        self.ax.bar(self.x, self.y)

        self.ax.set_xlabel("phi (\u00D8)")
        self.ax.set_ylabel("weight %")