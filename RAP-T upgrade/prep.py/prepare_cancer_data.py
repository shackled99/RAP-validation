"""
Cancer Data Preparation Script - FIXED
=======================================

Processes downloaded cancer datasets into RAP-compatible format.

Author: The Potato Researcher 🥔
Date: November 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*70)
print("CANCER DATA PREPARATION - FIXED VERSION")
print("="*70)

cancer_dir = Path("datasets/cancer")
cancer_dir.mkdir(parents=True, exist_ok=True)

# ===================================================================
# 1. HL-60 Leukemia Growth Curves - FIXED
# ===================================================================
print("\n1. Processing HL-60 Leukemia Growth Curves...")

hl60_file = cancer_dir / "hl60_growth.csv"

if hl60_file.exists():
    try:
        # Read the HL-60 dataset
        df = pd.read_csv(hl60_file)
        
        print(f"   Loaded: {len(df)} rows")
        print(f"   Columns: {list(df.columns)}")
        
        # The data has multiple wells - need to separate them
        # Columns: row, col, well, cells, timepoint(days), timpoint(hr), average, total, cell percent
        
        # Group by well to create separate curves
        wells = df['well'].unique()
        print(f"   Found {len(wells)} unique wells")
        
        # Create output dataframe
        output_data = {}
        
        for well in wells:
            well_data = df[df['well'] == well].copy()
            
            # Sort by time to ensure monotonic
            well_data = well_data.sort_values('timpoint(hr)')
            
            # Use hour timepoints
            time_col = well_data['timpoint(hr)'].values
            cells_col = well_data['cells'].values
            
            # Check if we have good data
            if len(time_col) > 5 and not np.all(cells_col == 0):
                # Store this well's data
                output_data[f'Well_{well}'] = cells_col
        
        if output_data:
            # Get common time array (should be same for all wells)
            first_well = df[df['well'] == wells[0]].sort_values('timpoint(hr)')
            time_array = first_well['timpoint(hr)'].values
            
            # Create DataFrame
            output_df = pd.DataFrame(output_data)
            output_df.insert(0, 'Time (h)', time_array)
            
            # Save as Excel for RAP
            output_file = cancer_dir / "hl60_processed.xlsx"
            output_df.to_excel(output_file, index=False)
            
            print(f"\n   ✅ Saved to: {output_file}")
            print(f"   Format: {len(output_data)} wells with {len(time_array)} time points each")
            
        else:
            print(f"   ⚠️ No valid well data found")
        
    except Exception as e:
        print(f"   ❌ Error processing HL-60: {str(e)}")
        import traceback
        traceback.print_exc()

else:
    print(f"   ⚠️ File not found: {hl60_file}")

# ===================================================================
# 2. DepMap Sample Info (Doubling Times)
# ===================================================================
print("\n2. Processing DepMap Sample Info...")

depmap_file = cancer_dir / "depmap_sample_info.csv"

if depmap_file.exists():
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                df = pd.read_csv(depmap_file, encoding=encoding)
                print(f"   Loaded with {encoding} encoding: {len(df)} cell lines")
                break
            except:
                continue
        
        print(f"   Columns: {list(df.columns[:10])}...")
        
        # Filter for lines with doubling time data
        if 'doubling_time' in df.columns:
            df_with_dt = df[df['doubling_time'].notna()]
            print(f"   Cell lines with doubling time: {len(df_with_dt)}")
            
            # Save processed version
            output_file = cancer_dir / "depmap_processed.csv"
            df_with_dt.to_csv(output_file, index=False)
            
            print(f"   ✅ Saved to: {output_file}")
        else:
            print(f"   ⚠️ 'doubling_time' column not found")
            
    except Exception as e:
        print(f"   ❌ Error processing DepMap: {str(e)}")

else:
    print(f"   ⚠️ File not found: {depmap_file}")

# ===================================================================
# Summary
# ===================================================================
print("\n" + "="*70)
print("PREPARATION COMPLETE")
print("="*70)

processed_files = list(cancer_dir.glob("*_processed.*"))

if processed_files:
    print("\nProcessed files ready for RAP analysis:")
    for f in processed_files:
        print(f"   ✅ {f.name}")
    
    print("\nNext steps:")
    print("1. Restart Streamlit explorer")
    print("2. Select hl60_leukemia dataset")
    print("3. Run RAP fits on cancer cells")
    print("4. Compare to E. coli baseline (85%)")

else:
    print("\n⚠️ No processed files created")

print("="*70)
