"""
Quick diagnostic to check Excel columns
"""
import pandas as pd

file_path = r"datasets\biological\ecoli_data\BW25113_Growth_Round01.xlsx"

print("Reading Excel file...")
df = pd.read_excel(file_path)

print(f"\nTotal columns: {len(df.columns)}")
print(f"\nFirst 20 column names:")
for i, col in enumerate(df.columns[:20], 1):
    print(f"  {i}. {col}")

print(f"\nColumn names containing 'time' (case-insensitive):")
time_cols = [col for col in df.columns if 'time' in str(col).lower()]
print(time_cols if time_cols else "  None found")

print(f"\nColumn names containing 'OD' (case-sensitive):")
od_cols = [col for col in df.columns if 'OD' in str(col)]
print(od_cols if od_cols else "  None found")

print(f"\nColumn names containing 'od' (case-insensitive):")
od_cols_lower = [col for col in df.columns if 'od' in str(col).lower()]
print(od_cols_lower if od_cols_lower else "  None found")

print(f"\nAll column names:")
for col in df.columns:
    print(f"  '{col}'")
