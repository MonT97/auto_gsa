import os

from .defaults import Defaults

from typedefs import GraphType, SaveObject
from helpers import Analyzer, Plotter
from models import Sample

import matplotlib.pyplot as plt
import pandas as pd

class CanSave(Defaults):
    """
    A mixin wrapping the saving functionality.
    - save_resutlts.
    """
    def cs_save_results(self, sample: Sample,
                        raw_dir: str, save_obj: SaveObject, rounding: int = 3) -> None:
        """
        Saves the results graphs and spreadsheets to desk.
        - raw_dir: the dirctory that contains the raw result files, [svg] graphs and [csv] spreadsheets.
        - rounding: rounding the values in the output sheet.
        - The fallowing are within a SaveObject:
            - results_dir: the directory to contain the processed result files.
            - result_folder_name: the name of the results files containing folder.
            - prfx: a prefix to append to the resulting spreadsheets name.
            _ clr: the color of the graphs/plots.
        """
        _clr = save_obj.color
        _prfx = save_obj.prefix
        _results_path = save_obj.results_path
        _result_folder_name = save_obj.results_folder_name
        _save_raws = save_obj.raw_files

        _result_file_name: str = _prfx+sample.get_name().lower()
        _results_dir: str = os.path.join(_results_path, _result_folder_name)
        _raw_results_dir: str = os.path.join(_results_dir, raw_dir) #!rawThing

        _file_path: str = os.path.join(_results_dir, _result_file_name)
        _raw_file_path: str = os.path.join(_raw_results_dir, _result_file_name)

        _sample_data: pd.DataFrame = sample.get_data()

        _ana: Analyzer = Analyzer(_sample_data)
        _method = pd.DataFrame({'0': ['Analysis method:'], '1': [_ana.get_method().value]})
        _stats = _ana.get_stats().to_frame()
        _interp = _ana.get_interpretation().to_frame()

        if not os.path.exists(_results_dir):
            os.mkdir(_results_dir)
        
        with pd.ExcelWriter(f'{_file_path}.xlsx', engine='openpyxl', mode='w') as writer:
            _sample_data.to_excel(writer, index=False, sheet_name='data')
            _method.to_excel(writer, index=False, header=False, sheet_name='stats')
            _stats.to_excel(writer, index=False, float_format=f'%.{rounding}f',
                            merge_cells=False, startrow=_method.shape[0]+1, sheet_name='stats')
            _interp.to_excel(writer, index=False,
                            merge_cells=False, startrow=_method.shape[0]+_stats.shape[0]+3,
                            sheet_name='stats')
        
        if not os.path.exists(_raw_results_dir) and _save_raws: 
            os.mkdir(_raw_results_dir)
            _sample_data.to_csv(f'{_raw_file_path}.csv', index=False)

        for _type in GraphType:
            _graph_names = {GraphType.HIST: "Histogram", GraphType.CUM: "Cumulative Curve"}
            _title: str = _graph_names[_type]
            _graph_file_name: str = f'{sample.get_name().lower()}_{_title.lower().replace(' ', '_')}'
            _graph_file_path: str = os.path.join(_results_dir, _graph_file_name)
              
            _fig, _ax = plt.subplots()
            _fig.set_layout_engine('constrained')
            _x, _y, _points, _method = _ana.get_plot_data(_type)
            Plotter(_x, _y, _points, _ax, _type, _method, _clr)
            _ax.set_title(f'{sample.get_name()}\n{_title}')
            _fig.savefig(_graph_file_path+'.png', dpi=300, format='png')
          
            if _save_raws:
                _raw_graph_file_path: str = os.path.join(_raw_results_dir, _graph_file_name)
                _fig.savefig(_raw_graph_file_path+'.svg', dpi=300, format='svg')
          
            plt.close()