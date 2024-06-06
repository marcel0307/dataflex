# custom_andas.py

import polars as pl
import pandas as pd

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
    
class FallbackBase:
    def __init__(self, data):
        self.data = data

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

    def __getattr__(self, name):
        def method(*args, **kwargs):
            try:
                result = getattr(self.data, name)(*args, **kwargs)
                if isinstance(result, (pl.DataFrame, pl.Series)):
                    return self.__class__(result)
                return result
            except Exception as e:
                print(f"Fallback to pandas applied, due to Error {type(e)}: {e}")
                pandas_data = self._convert_to_pandas()
                result = getattr(pandas_data, name)(*args, **kwargs)
                if isinstance(result, (pd.DataFrame, pd.Series)):
                    return self.__class__(self._convert_to_polars(result))
                return result

        return method


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

class PolarsPandasProxy(FallbackBase):
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


    def __getitem__(self, key):
        try:
            result = self.data[key]
            if isinstance(result, (pl.DataFrame, pl.Series)):
                return PolarsPandasProxy(result)
            return result
        except (KeyError, TypeError):
            pandas_data = self._convert_to_pandas()
            result = pandas_data[key]
            return PolarsPandasProxy(self._convert_to_polars(result))

    def __repr__(self):
        return repr(self.data)
    
    @property
    def loc(self):
        return Locator(self.data)
    
    @property
    def str(self):
        return StringMethods(self)


class Locator(FallbackBase):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            data = self.data.slice(key.start, key.stop - key.start)
        elif isinstance(key, list):
            data = self.data.filter(pl.col('index').is_in(key))
        elif isinstance(key, PolarsPandasProxy):  # Change this line
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
    return PolarsPandasProxy(data)

def Series(data=None, index=None, dtype=None, name=None, copy=False, fastpath=False):
    if isinstance(data, pd.Series):
        data = pl.from_pandas(data)
    return PolarsPandasProxy(data)