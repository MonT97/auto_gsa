from typedefs import GraphType, SkewnessSchema, SamplePoints, SampleStats, PlotInput, PlotData, StatsInterpretation, AnalysisMethod

from scipy.interpolate import PchipInterpolator
from collections.abc import Callable

import pandas as pd
import numpy as np

class Analyzer():
    """
    The class that wrangles the data, provides the stats it's interpretation, then prepares it for plotting.
    """
    #TODO: emplement Sample() like memory
    stats_list: list[SampleStats] = []

    def __init__(self, sample_data: pd.DataFrame) -> None:
        
        self.sample_data = sample_data # edge case discoverd when testing friedman 1958 
        self.x, self.y, interp_f = self._get_input(self.sample_data)
        self.points, self.stats = self._calculate_stats(self.y, interp_f)

        #TODO: expose to user edit!
        _default_skewness_schema: SkewnessSchema = SkewnessSchema.OBSERVATION
        self.interpretation = self._interperate(self.stats, _default_skewness_schema)

    def _get_input(self,
                   sample_data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, PchipInterpolator]:
        """
        Prepares the data [phi, cum.wt%] for stats calculation via interpolation using Scipy's PchipInterpolator, an implementation of Hermite plynomial interpolation.
        - -> (interpolated_phi, interpolated_cum.wt%, interpolation_function)
        """
        sample_data = sample_data.dropna()
        _phi: pd.Series = sample_data['phi']
        _cum_wht: pd.Series = sample_data['cum.wht%']

        def _inverse(
                interpolation_fn: PchipInterpolator,
                wt_prcnts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            """
            Interpolation function inversion, get phi(x) at wt_prcnts(y).
            - -> tuple[phis, wt_prcnts]
            """
            _rounding_digits: int = 4
            _phis_inversed: list[float] = []
            _valid_wt_prcnts: list[float] = []

            for _wt_prcnt in wt_prcnts:
                _phi = interpolation_fn.solve(_wt_prcnt)
                # an edge case discoverd when testing friedman 1958, it seems that the PCHIP interp. doesn't solve for the very first and last data points.
                if len(_phi) < 3:
                    continue
                _phis_inversed.append(_phi[1])
                _valid_wt_prcnts.append(_wt_prcnt)
                
            _x: np.ndarray = np.round(_phis_inversed, _rounding_digits)
            _y: np.ndarray = np.round(_valid_wt_prcnts, _rounding_digits)

            return (_x, _y)
        
        _interp_f = PchipInterpolator(_phi, _cum_wht)
        _cap: float = _cum_wht.max()
        _min: float = _cum_wht.min()
        _step: int = int(_cap)*100
        _lerp_y = np.linspace(_min, _cap, _step, endpoint=False)

        _x, _y = _inverse(_interp_f, _lerp_y) 

        return (_x, _y, _interp_f)

    def _calculate_stats(self,
            y: np.ndarray, interp_f: PchipInterpolator
            ) -> tuple[SamplePoints, SampleStats]:
        """
        Calculates stats: [mean, std, skewness, kurtosis], based on ,if possible, (Folk&Ward, 1957) graphical formulas, otherwise, the Method of Moments is used.
        - y: [cum.wht%].min()
        - interp_f: [the interpolation function]
        """
        _points: SamplePoints = []
        _stats: SampleStats = SampleStats()
        _wt_prcnts: list[float] = [5.0, 16.0, 25.0, 50.0, 75.0, 84.0, 95.0]

        #? 2 or less points sample produces empty [y] from _get_input():
        if not y.size:
            self.method = AnalysisMethod.TWOPOINTS
            _stats.mean = self.sample_data['phi'].mean()
        
        else:
            _create_point: Callable = lambda wt_prcnt: (wt_prcnt, interp_f.solve(wt_prcnt)[1])
            _points = [_create_point(wt_prcnt) for wt_prcnt in _wt_prcnts if wt_prcnt > y.min()]

            _graphical_is_valid: bool = len(_points) == len(_wt_prcnts)

            if _graphical_is_valid:
                self.method = AnalysisMethod.GRAPHICAL

                _phi_prcnt: dict[str, float] = {f'{int(k)}': v for (k), v in _points}
                _get_phi: Callable = lambda phi: _phi_prcnt[f'{phi}']

                _stats.mean = (_get_phi(16)+_get_phi(50)+_get_phi(84))/3
                _stats.std = (((_get_phi(84)-_get_phi(16))/4)+((_get_phi(95)-_get_phi(5))/6.6))
                _stats.skewness = (
                                    ((_get_phi(16)+_get_phi(84)-(2*_get_phi(50)))/
                                    (2*(_get_phi(84))-_get_phi(16)))+
                                    (_get_phi(5)+_get_phi(95)-(2*_get_phi(50)))/
                                    (2*(_get_phi(95))-_get_phi(5))
                                    )
                _stats.kurtosis = ((_get_phi(95)-_get_phi(5))/(2.44*(_get_phi(75)/_get_phi(25))))
                
            else:
                self.method = AnalysisMethod.MOMENTS
                #TODO: I assume a 100g sample, universalize!
                _original_sample_wht: float = 100.0 # float is to allow for measurement error +- .1g

                _phis = self.sample_data['phi']
                _get_midpoint: Callable = lambda x: (_phis[x]+_phis[x+1])/2
                _d: np.ndarray = np.append([_get_midpoint(i) for i in range(len(_phis)-1)], _phis.max())
                _f: np.ndarray = self.sample_data['wht%'].to_numpy()
                _pan_fraction: float = _original_sample_wht - _f.sum()

                if _pan_fraction < 5.0:
                    _N = _f.sum() #? some say N=100, yet this is after analytical_sedimentology book

                    _stats.mean = np.sum(_f*_d)/_N
                    _stats.std = (np.sum(_f*((_d-_stats.mean)**2))/_N)**.5
                    _stats.skewness = np.sum(_f*((_d-_stats.mean)**3))/(_N*_stats.std**3)
                    _stats.kurtosis = np.sum(_f*((_d-_stats.mean)**4))/(_N*_stats.std**4)
                
                #TODO: the (> 5.0) case is handled in the [_points] creation, analysis should be done with a caviate in the report and spreadsheet.
                # else:
                #     print(f'Pan fraction [{_pan_fraction}] >5%, The analysis is unreliable, disregard this sample!.')
        
        Analyzer.stats_list.append(_stats)
        
        return (_points,_stats)

    def _interperate(self, stats: SampleStats, skew_schema: SkewnessSchema) -> StatsInterpretation:
        """
        Interperate the sample stats according to [see the litrature]
        - std ------> sorting.
        - skewness -> the dominent tail, coarse/fine.
        - kurtosis ---> gives an idea about peakedness the distribution, it usefullness is questionable, see (Fieller, 1984).
        """
        def _sorting(std: float) -> str:

            _sorting: str = ''

            if std < .35:
                _sorting = 'very well'
            elif .35 <= std <= .5:
                _sorting = 'well'
            elif .5 <= std <= .7:
                _sorting = 'moderatrly well'
            elif .7 <= std <= 1:
                _sorting = 'moderatrly'
            elif 1 <= std <= 2:
                _sorting = 'poorly'
            elif 2 <= std <= 4:
                _sorting = 'very poorly'
            else:
                _sorting = 'extremely poorly'
            
            return _sorting+' sorted'

        def _skew(skew: float, schema: SkewnessSchema) -> str:

            _skewness: str = ''

            def get_verbal_schema(schema: SkewnessSchema) -> tuple[str, str]:
                
                verbal_schema: tuple[str, str] = ('','')

                match schema:
                    case SkewnessSchema.ANASEDI:
                        verbal_schema = ('fine', 'coarse')
                    case SkewnessSchema.FOLKWARD57:
                        verbal_schema = ('positive', 'negative')
                    case SkewnessSchema.OBSERVATION:
                        verbal_schema = ('coarse', 'fine')

                return verbal_schema
            
            _verbal_schema: tuple[str, str] = get_verbal_schema(schema)

            if skew > .3:
                _skewness = f'strongly {_verbal_schema[0]} skewed'
            elif .3 >= skew >= .1:
                _skewness = f'{_verbal_schema[0]} skewed'
            elif .1 >= skew >= -.1:
                _skewness = f'near symmetrical'
            elif -.1 >= skew >= -.3:
                _skewness = f'{_verbal_schema[1]} skewed'
            else:
                _skewness = f'strongly {_verbal_schema[1]} skewed'
            
            return _skewness       

        def _kurtosis(kurt: float) -> str:

            _kurtosis: str = ''

            if kurt < .67:
                _kurtosis = 'very platy'
            elif .67 <= kurt <= .9:
                _kurtosis = 'platy'
            elif .9 <= kurt <= 1.11:
                _kurtosis = 'meso'
            elif 1.11 <= kurt <= 1.5:
                _kurtosis = 'lepto'
            elif 1.5 <= kurt <= 3:
                _kurtosis = 'very lepto'
            else:
                _kurtosis = 'extremely lepto'
            
            return _kurtosis+'kurtic'

        _interpretation: StatsInterpretation = StatsInterpretation()
        _interpretation.sorting = _sorting(stats.std)
        _interpretation.skewness = _skew(stats.skewness, skew_schema)
        _interpretation.kurtosis = _kurtosis(stats.kurtosis)
        
        return _interpretation

    def get_stats(self) -> SampleStats:
        """
        Returns the stats.
        """
        return self.stats

    def get_method(self) -> AnalysisMethod:
        """
        Retruns the analysis method used.
        - -> str
        """
        return self.method

    def get_interpretation(self) -> StatsInterpretation:
        """
        Returns the interpretation of the stats.
        """
        return self.interpretation

    def get_plot_data(self, graph_type: GraphType) -> PlotData:
        """
        Returns the plot ready data.
        - -> [x, y], points, analysis_method]
        """
        match graph_type:
            case GraphType.HIST:
                _x: PlotInput = self.sample_data['phi']
                _y: PlotInput = self.sample_data['wht%']
            case GraphType.CUM:
                _x: PlotInput = self.x
                _y: PlotInput = self.y

        return (_x, _y, self.points, self.method)