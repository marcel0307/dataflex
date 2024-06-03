import polars as pl

class DataFrame:
    def __init__(self, data:dict) -> None:
        self._df = pl.DataFrame(data)

    def head(self, n=5):
        return self._df.head(n)
    