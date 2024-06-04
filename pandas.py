# pandas.py

import polars as pl

class Base:
    def __init__(self, data):
        self.data = data

    def head(self, n=5):
        return self.data.head(n)

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

class Series(Base):
    def __init__(self, data: list) -> None:
        super().__init__(pl.Series(data))

    
