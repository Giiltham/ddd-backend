import pandas as pd

# Load the dataset
df = pd.read_csv("datasets/charts.csv")

# Count appearances of each artistName per country_iso2
duplicates = (
    df.groupby(["artistName", "country_iso2"])
    .size()
    .reset_index(name="count")
    .query("count > 1")
)

print(duplicates.head())
