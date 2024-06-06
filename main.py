import custom_pandas as pd

# Example usage
custom_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

# This will use the custom pandas method implemented using polars
print(custom_df.head())

# This will fallback to real pandas if the custom method is not implemented or fails
print(custom_df.apply(lambda x: x ** 2))

data = {
    'colA': [1, 2, 4, 7, 10],
    'colB': [10, 20, 30, 40, 50],
    'index': [4, 5, 6, 7, 8],
    'test': ["abc", "joij", "def", "iji", "ioj"]
}
df = pd.DataFrame(data)

print(df.head())


# List of labels
print(df.loc[[4, 6], ['colA', 'colB']].head())

# Slice
print(df.loc[4:7].head())

# Boolean Series
bool_series = pd.Series([True, False, True, False, True])
print(df.loc[bool_series].head())

# Callable function
print(df.loc[lambda df: df['colA'] > 2].head())

print(df[(df["test"].str.lower() == "abc") | (df["test"].str.lower() == "def")].head())