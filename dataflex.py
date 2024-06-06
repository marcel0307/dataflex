# custom_andas.py

import polars as pl
import pandas as pd
    
class BaseProxy:
    def __init__(self, data):
        if isinstance(data, dict):
            self.data = pl.DataFrame(data)
        elif isinstance(data, list):
            self.data = pl.Series(data)
        elif isinstance(data, (pl.DataFrame, pl.Series)):
            self.data = data
        elif isinstance(data, (pd.DataFrame, pd.Series)):
            self.data = pl.from_pandas(data)
        else:
            raise ValueError("Unsupported data type")
        
    def _fallback(self, operation, key, *args, **kwargs):
        try:
            result = operation(*args, **kwargs)
            if isinstance(result, (pl.DataFrame, pl.Series)):
                return BaseProxy(result)
            return result
        except (KeyError, TypeError, Exception) as e:
            print(f"Fallback to pandas applied, due to Error {type(e)}: {e}")
            pandas_data = self._convert_to_pandas()
            result = getattr(pandas_data, key)(*args, **kwargs)
            if isinstance(result, (pd.DataFrame, pd.Series)):
                return BaseProxy(self._convert_to_polars(result))
            return result
        
    def _convert_to_pandas(self):
        if isinstance(self.data, pl.DataFrame):
            return self.data.to_pandas()
        elif isinstance(self.data, pl.Series):
            return pd.Series(self.data.to_list())
        else:
            return self.data

    def _convert_to_polars(self, data):
        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return pl.from_pandas(data)
        else:
            return data

    def __repr__(self):
        return repr(self.data)
    
    def __getitem__(self, key):
        return self._fallback(lambda: self.data[key], key)

    def __getattr__(self, name):
        def method(*args, **kwargs):
            return self._fallback(lambda: getattr(self.data, name)(*args, **kwargs), name, *args, **kwargs)
        return method
    
    @property
    def loc(self):
        return Locator(self.data)
    
    @property
    def str(self):
        return StringMethods(self)


class DataFrame(BaseProxy):
    def __init__(self, data: dict) -> None:
        super().__init__(pl.DataFrame(data))

    def merge(self, df_right, how: str, on: str):
        return DataFrame(self.data.join(df_right.data, how=how, on=on))
    
class StringMethods:
    def __init__(self, series):
        self.series = series

    def lower(self):
        return Series(self.series.data.str.to_lowercase())

class Series(BaseProxy):
    def __init__(self, data: list) -> None:
        super().__init__(pl.Series(data))

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


class Locator(BaseProxy):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            data = self.data.slice(key.start, key.stop - key.start)
        elif isinstance(key, list):
            data = self.data.filter(pl.col('index').is_in(key))
        elif isinstance(key, BaseProxy):  # Change this line
            data = self.data.filter(key.data)
        elif callable(key):
            data = self.data.filter(key(self.data))
        else:
            data = self.data.filter(pl.col('index') == key)

        if isinstance(self.data, pl.DataFrame):
            return DataFrame(data)
        else:
            return Series(data)
            


def DataFrame(data=None, index=None, columns=None, dtype=None, copy=False):
    if isinstance(data, pd.DataFrame):
        data = pl.from_pandas(data)
    return BaseProxy(data)

def Series(data=None, index=None, dtype=None, name=None, copy=False, fastpath=False):
    if isinstance(data, pd.Series):
        data = pl.from_pandas(data)
    return BaseProxy(data)