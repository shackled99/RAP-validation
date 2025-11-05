"""Quick debug script to see what's in the Excel file"""

import pandas as pd

print("🔍 DEBUGGING EXCEL FILE STRUCTURE")
print("="*70)

# Load first file
df = pd.read_excel('ecoli_data/BW25113_Growth_Round01.xlsx', sheet_name=0)

print(f"\n📊 DataFrame shape: {df.shape}")
print(f"\n📊 First 10 column names:")
for i, col in enumerate(df.columns[:10]):
    print(f"  {i}: '{col}'")

print(f"\n📊 First 5 rows, first 3 columns:")
print(df.iloc[:5, :3])

print(f"\n📊 Data types:")
print(df.dtypes[:5])

print(f"\n📊 Check for NaN in first data column:")
col_name = df.columns[1]
print(f"  Column name: '{col_name}'")
print(f"  First 10 values: {df[col_name].values[:10]}")
print(f"  All NaN? {df[col_name].isna().all()}")
print(f"  Any NaN? {df[col_name].isna().any()}")

print("\n✅ Debug complete!")
