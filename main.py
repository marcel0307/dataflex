import pandas as pd
import polars as pl
if __name__ == "__main__":
    data = {
        'colA': [1,2,3],
        'colB': [4,5,6],
    }
    df = pd.DataFrame(data)

    print(df.head())