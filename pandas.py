# pandas.py

import polars as pl

class Base:
    def __init__(self, data):
        self.data = data

    def head(self, n=5):
        return self.data.head(n)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return Series(self.data[key])
        elif isinstance(key, list):
            if all(isinstance(item, str) for item in key):
                return self.__class__({item: self.data[item] for item in key})
            else:
                raise TypeError("All elements in the list must be of type str")
        elif isinstance(key, Series):
            return self.__class__(self.data.filter(key.data))
        else:
            raise TypeError(f"Indices must be str, list of str, or Series, not {type(key)}")

    @property
    def loc(self):
        return Locator(self.data)

class Locator:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            data = self.data.slice(key.start, key.stop - key.start)
        elif isinstance(key, list):
            data = self.data.filter(pl.col('index').is_in(key))
        elif isinstance(key, Series):
            data = self.data.filter(key.data)
        elif callable(key):
            data = self.data.filter(key(self.data))
        else:
            data = self.data.filter(pl.col('index') == key)

        return data

class DataFrame(Base):
    def __init__(self, data: dict) -> None:
        super().__init__(pl.DataFrame(data))

    def merge(self, df_right, how: str, on: str):
        return DataFrame(self.data.join(df_right.data, how=how, on=on))
    
class StringMethods:
    def __init__(self, series):
        self.series = series

    def lower(self):
        return Series(self.series.data.str.to_lowercase())

class Series(Base):
    def __init__(self, data: list) -> None:
        super().__init__(pl.Series(data))

    @property
    def str(self):
        return StringMethods(self)

    def __eq__(self, other):
        if isinstance(other, str):
            return Series(self.data == other)
        elif isinstance(other, Series):
            return Series(self.data == other.data)

    def __or__(self, other):
        if isinstance(other, Series):
            return Series(self.data | other.data)
        
    def __and__(self, other):
        if isinstance(other, Series):
            return Series(self.data & other.data)

    
