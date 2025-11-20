"""
Healthy Cell Data Preparation
==============================

Processes healthy (normal) cell growth data into RAP format.

Place your downloaded files in datasets/healthy_cells/
This script will convert them to RAP-compatible format.

Author: The Potato Researcher 🥔
Date: November 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

print("="*70)
print("HEALTHY CELL DATA PREPARATION")
print("="*70)

healthy_dir = Path("datasets/healthy_cells")
healthy_dir.mkdir(parents=True, exist_ok=True)

# Find all data files
csv_files = list(healthy_dir.glob("*.csv"))
excel_files = list(healthy_dir.glob("*.xlsx")) + list(healthy_dir.glob("*.xls"))

all_files = csv_files + excel_files

if not all_files:
    print("\n⚠️  No data files found in datasets/healthy_cells/")
    print("\nPlease download healthy cell growth data and place it here:")
    print("  - MCF-10A growth curves (normal breast)")
    print("  - MRC-5 growth curves (lung fibroblasts)")
    print("  - Other normal cell lines")
    print("\nSee SEARCH_GUIDE.txt for download instructions")
    print("="*70)
    exit()

print(f"\nFound {len(all_files)} file(s) to process:")
for f in all_files:
    print(f"  - {f.name}")

print("\n" + "="*70)

processed_count = 0

for filepath in all_files:
    print(f"\nProcessing: {filepath.name}")
    print("-" * 70)
    
    try:
        # Read file
        if filepath.suffix == '.csv':
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns[:10])}" + ("..." if len(df.columns) > 10 else ""))
        
        # Try to identify time and measurement columns
        time_col = None
        for col in df.columns:
            if any(term in str(col).lower() for term in ['time', 'day', 'hour']):
                time_col = col
                break
        
        if time_col:
            print(f"  Time column: '{time_col}'")
        else:
            print(f"  ⚠️  No time column detected - you may need to manually specify")
            continue
        
        # Find measurement columns (everything except time)
        measure_cols = [col for col in df.columns if col != time_col]
        
        # Filter for numeric columns
        measure_cols = [col for col in measure_cols if df[col].dtype in ['int64', 'float64']]
        
        print(f"  Measurement columns: {len(measure_cols)}")
        if measure_cols:
            print(f"    Examples: {measure_cols[:5]}")
        
        if not measure_cols:
            print(f"  ⚠️  No measurement columns found")
            continue
        
        # Create standardized output
        output_df = df[[time_col] + measure_cols].copy()
        
        # Rename time column to standard
        output_df.rename(columns={time_col: 'Time (h)'}, inplace=True)
        
        # Save as Excel for RAP
        output_name = filepath.stem + "_processed.xlsx"
        output_path = healthy_dir / output_name
        
        output_df.to_excel(output_path, index=False)
        
        print(f"  ✅ Saved to: {output_path.name}")
        print(f"     Format: Time + {len(measure_cols)} growth curve(s)")
        
        processed_count += 1
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        continue

print("\n" + "="*70)
print("PROCESSING SUMMARY")
print("="*70)

print(f"\nProcessed: {processed_count}/{len(all_files)} files")

processed_files = list(healthy_dir.glob("*_processed.xlsx"))

if processed_files:
    print(f"\nReady for RAP analysis:")
    for f in processed_files:
        print(f"  ✅ {f.name}")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Add to config/datasets.json:
   
   "mcf10a_healthy": {
     "name": "MCF-10A Normal Breast Cells",
     "organism": "Human mammary epithelial (normal)",
     "file_pattern": "mcf10a_*_processed.xlsx",
     "data_directory": "datasets/healthy_cells",
     "time_column_patterns": ["Time"],
     "od_column_patterns": ["Cell", "Count", "OD"],
     "expected_convergence": 0.85
   }

2. Test in explorer:
   streamlit run explore_rap.py
   
3. Compare results:
   - E. coli: ~85%
   - Healthy cells: ~85% (hypothesis)
   - Cancer cells: >90% (hypothesis)
   
4. Run batch analysis:
   python run_rap.py mcf10a_healthy
    """)
else:
    print("\n⚠️  No files successfully processed")
    print("\nCheck the error messages above")
    print("You may need to manually format the data")

print("="*70)
