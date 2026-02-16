import pandas as pd

class Sample():
    '''
        The class resembling the sample:
            - name: str.
            - data: pd.DataFrame.
    '''
    samples_list: list = []
    def __init__(self, name: str = "", data: pd.DataFrame = pd.DataFrame()) -> None:
        
        self._name = name
        self._data = self._run_analysis(data)
    
    def __repr__(self) -> str:

        return f"{__class__.__name__} ({self._name=}, {self._data=})"
    
    def __eq__(self, other) -> bool:
        
        return True if (self._name == other._name) and (self._data == other._data) else False

    def _run_analysis(self, data: pd.DataFrame) -> pd.DataFrame:

        if not data.empty:
            data['wht%'] = ((data['wht']/data['wht'].sum())*100).round(2)
            data['cum.wht%'] = data['wht'].cumsum()
            Sample.samples_list.append(self)
        
        return data
    
    def get_name(self, full: bool = False) -> str:

        name: str = self._name.split(".")[0].capitalize()

        return name if not full else self._name      
    
    def get_data(self) -> pd.DataFrame:

        return self._data