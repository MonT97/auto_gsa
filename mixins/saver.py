import os
from typing import Final

import matplotlib.pyplot as plt
import pandas as pd

from models import Analyzer, Sample
from typedefs import GraphType, SaveObject

from .defaults import Defaults
from .plotter import CanPlot

# Constants:

# graph:
WIDTH_PER_X: Final[float] = .71*.75 # test driven, 6.4[default graph width]/9[len(x)] in the sample.
EDGE_PADDING: Final[float] = 10/72

class CanSave(Defaults, CanPlot):
    """
    A mixin wrapping the saving functionality.
    - save_results.
    """
    def cs_save_results(self, sample: Sample, raw_dir: str,
                        save_obj: SaveObject, rounding: int = 3) -> None:
        """
        Part of the CanSave mixin.
        Saves the results graphs and spreadsheets to desk.
        - raw_dir: the directory that contains the raw result files, [svg] graphs and [csv] spreadsheets.
        - rounding: rounding the values in the output sheet.
        - The fallowing are within a SaveObject:
            - prefix: To append to the beginning of the file's name.
            - results_path: To save the file within.
            - results_folder_name: The dir name.
            - color: The color of graph elements.
            - dpi: The png resolution.
            - save_raw_files: If True a non interpreted spreadsheet would be exported as well.
            - interval: To inclusively export files between which.
        """
        # Unpacking the SaveObj:
        _clr = save_obj.color
        _prfx = save_obj.prefix
        _results_path = save_obj.results_path
        _result_folder_name = save_obj.results_folder_name
        _save_raws = save_obj.save_raw_files
        _dpi = save_obj.dpi
        _transparent = save_obj.transparent

        # Paths:
        _result_file_name: str = _prfx+sample.get_name().lower()
        _results_dir: str = os.path.join(_results_path, _result_folder_name)
        _raw_results_dir: str = os.path.join(_results_dir, raw_dir) #!rawThing
       
        if not os.path.exists(_results_dir):
            os.mkdir(_results_dir)

        _file_path: str = os.path.join(_results_dir, _result_file_name)
        _raw_file_path: str = os.path.join(_raw_results_dir, _result_file_name)

        # Data:
        _sample_data: pd.DataFrame = sample.get_data()

        _ana: Analyzer = Analyzer(_sample_data)
        _method = pd.DataFrame({'0': ['Analysis method:'], '1': [_ana.get_method().value]})
        _stats = _ana.get_stats().to_frame()
        _interp = _ana.get_interpretation().to_frame()

        # Writing Data:
        with pd.ExcelWriter(f'{_file_path}.xlsx', engine='openpyxl', mode='w') as writer:
            _sample_data.to_excel(writer, index=False, sheet_name='data')
            _method.to_excel(writer, index=False, header=False, sheet_name='stats')
            _stats.to_excel(writer, index=False, float_format=f'%.{rounding}f',
                            merge_cells=False, startrow=_method.shape[0]+1, sheet_name='stats')
            _interp.to_excel(writer, index=False,
                            merge_cells=False, startrow=_method.shape[0]+_stats.shape[0]+3,
                            sheet_name='stats')
            
        for _type in GraphType:
            _graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}
            _sample_name: str = sample.get_name().lower()
            _title: str = _graph_names[_type]
            _graph_file_name: str = f'{_sample_name}_{_title.lower().replace(' ', '_')}'
            _graph_file_path: str = os.path.join(_results_dir, _graph_file_name)
            
            _x, _y, _points, _method = _ana.get_plot_data(_type)
            # for samples analyzed with in extensive sieve set.
            _graph_width: float = len(_x)*WIDTH_PER_X if _type == GraphType.HIST else 6.8
            _fig, _ax = plt.subplots(figsize=(_graph_width,4.8), layout='constrained')
            _fig.get_layout_engine().set(h_pad=EDGE_PADDING, w_pad=EDGE_PADDING*2) #type: ignore

            self.cp_plot(_x, _y, _points, _method, _ax, _type, _clr)
            _ax.set_title(f'{sample.get_name()}\n{_title}')
            
            _fig.savefig(_graph_file_path+'.png', dpi=_dpi, format='png', transparent=_transparent)
          
            if _save_raws:
                if not os.path.exists(_raw_results_dir):
                    os.mkdir(_raw_results_dir)

                _sample_data.to_csv(f'{_raw_file_path}.csv', index=False)
                
                _raw_graph_file_path: str = os.path.join(_raw_results_dir, _graph_file_name)
                _fig.savefig(_raw_graph_file_path+'.svg', dpi=_dpi, format='svg')
          
            plt.close()