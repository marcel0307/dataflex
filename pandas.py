import polars as pl

class DataFrame:
    """
    DataFrame class that has the exact same user interface as pandas, but executing Polars transformations under the hood.
    """
    def __init__(self, data: dict) -> None:
        self._df = pl.DataFrame(data)

    def head(self, n=5):
        return self._df.head(n)

    def merge(self, df_right, how: str, on: str):
        return DataFrame(self._df.join(df_right._df, how=how, on=on))

    @property
    def loc(self):
        return DataFrameLocator(self._df)

class DataFrameLocator:
    def __init__(self, df):
        self.df = df

    def __getitem__(self, key):
        # Case 1: Single label (scalar)
        if not isinstance(key, tuple):
            key = (key, slice(None))

        # Case 2: Tuple (row_key, col_key)
        row_key, col_key = key

        # Handle row selection
        # TODO: check if slice start/stop need to be inclusive or exclusive
        if isinstance(row_key, slice):
            df = self.df.slice(row_key.start, row_key.stop - row_key.start)
        elif isinstance(row_key, list):
            df = self.df.filter(pl.col('index').is_in(row_key))
        elif isinstance(row_key, pl.Series):
            df = self.df.filter(row_key)
        elif callable(row_key):
            df = self.df.filter(row_key(self.df))
        else:
            df = self.df.filter(pl.col('index') == row_key)

        # Handle column selection
        if isinstance(col_key, slice):
            col_key = self.df.columns[col_key]
        elif callable(col_key):
            col_key = [col for col in self.df.columns if col_key(self.df[col])]

        return df.select(col_key)
