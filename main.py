import pandas as pd
import polars as pl
if __name__ == "__main__":
    data_left = {
        'colA': [1,2,3],
        'colB': [4,5,6]
    }
    df_left = pd.DataFrame(data_left)

    data_right = {
        'colA': [1,2,4],
        'index': [4,5,6]
    }
    df_right = pd.DataFrame(data_right)

    e = df_right.loc[4]
    print(e.head())