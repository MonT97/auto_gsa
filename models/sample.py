from dataclasses import dataclass
import pandas as pd


class Sample():
    '''
        The class resembling the sample:
            - name: str.
            - data: pd.DataFrame..
    '''
    samples_list: list = []
    def __init__(self, name: str = "", data: pd.DataFrame = pd.DataFrame()) -> None:
        
        self._name = name
        self._data = data
        self.run_analysis()
        Sample.samples_list.append(self)

    def __repr__(self) -> str:

        return f"{__class__.__name__} (name={self._name}, data={self._data})"
    
    def get_name(self, full: bool = False) -> str:

        name: str = self._name.split(".")[0].capitalize()

        return name if not full else self._name      
    
    def get_data(self) -> pd.DataFrame:

        return self._data

    def run_analysis(self) -> None:

        self._data['wht%'] = ((self._data['wht']/self._data['wht'].sum())*100).round(2)
        #? What effect does this have on the interpolatoin results?. No so it doesn't matter
        #? Move this to the Analysis() as it is a requirement for the method of moments
        #? maybe show the pure data and use this for calculations??
        if self._data['wht'].sum() < 100:
            self._data.iloc[-1, 1] += 100 - self._data['wht'].sum()

        self._data['cum.wht%'] = self._data['wht'].cumsum()