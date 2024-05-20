from dataclasses import dataclass
import pandas as pd

@dataclass
class Sample():
    '''
        The class resembling the sample
    '''
    def __repr__(self) -> str:
        return f"Sample(name= {self._name}, data={self._data})"

    def __init__(self, name: str = "", data: pd.DataFrame = pd.DataFrame()) -> None:
        
        self._name = name
        self._data = data
        self.run_analysis()

    def get_name(self) -> str:

        return self._name.split(".")[0].capitalize()
    
    def get_full_name(self) -> str:

        return self._name
    
    def get_data(self) -> pd.DataFrame:

        return self._data

    def run_analysis(self):

        self._data['wht%'] = (self._data['wht']/self._data['wht'].sum()).round(2)
        self._data['cum.wht%'] = self._data['wht'].cumsum()