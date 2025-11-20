import pandas as pd
df = pd.read_csv('../results/raw/full_scale_rap_results_n12547.csv', nrows=5)
print("Columns:", list(df.columns))
print("\nFirst few rows:")
print(df.head())
