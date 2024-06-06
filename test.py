from dataflex import DataFrame, Series

# Sample data for testing
data_dict = {
    'A': [1, 2, 3, 4, 5],
    'B': [5, 4, 3, 2, 1]
}

# Test DataFrame creation and head method
df = DataFrame(data_dict)
print("Polars head (should work):")
print(df.head())

# Test __getitem__ method for column selection
print("Column selection (should work):")
print(df['A'].head())

# Test __getitem__ method for row slicing
print("Row slicing using loc (should work):")
print(df.loc[1:3].head())

# Test merge operation
data_dict2 = {
    'A': [3, 4, 5, 6],
    'C': [7, 8, 9, 10]
}
df2 = DataFrame(data_dict2)
print("Merge DataFrame (should work):")
print(df.merge(df2, how='inner', on='A').head())

# Test Series string method lower (should fallback to pandas)
series_data = ["Hello", "World"]
series = Series(series_data)
print("String lower (should fallback to pandas):")
print(series.str.lower().head())

# Test Series equality comparison (should fallback to pandas)
series2 = Series(["hello", "world"])
print("Series equality comparison (should fallback to pandas):")
print(series == series2)

# Test Series logical operations (should fallback to pandas)
print("Series logical OR (should fallback to pandas):")
print(series | series2)

print("Series logical AND (should fallback to pandas):")
print(series & series2)
