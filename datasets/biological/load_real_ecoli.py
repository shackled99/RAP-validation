"""
Real E. coli Data Loader - Aida et al. (2025)
==============================================

Loads the "Bacterial growth profiles across one-thousand chemical-defined media"
dataset from Figshare.

Dataset: 13,608 growth curves from E. coli BW25113 strain
Source: Aida et al., 2022, eLife

Author: The Potato Researcher 🥔
Date: November 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_aida_ecoli_data(data_dir='ecoli_data', max_curves=None, rounds=None):
    """Load real E. coli growth data."""
    
    print(f"\n🔬 Loading Real E. coli Data (Aida et al., 2025)")
    print(f"=" * 70)
    
    # Find round files
    data_path = Path(data_dir)
    round_files = sorted(data_path.glob('BW25113_Growth_Round*.xlsx'))
    
    if not round_files:
        raise FileNotFoundError(f"No files found in {data_dir}")
    
    # Filter by rounds if specified
    if rounds is not None:
        round_files = [f for f in round_files if any(f'Round{r:02d}' in f.name for r in rounds)]
    
    print(f"📂 Found {len(round_files)} files")
    
    all_curves = {}
    time_array = None
    total_loaded = 0
    
    for round_file in round_files:
        round_num = int(round_file.stem.split('Round')[1])
        print(f"\n📊 Round {round_num:02d}: {round_file.name}")
        
        try:
            df = pd.read_excel(round_file, sheet_name=0)
            
            if time_array is None:
                time_array = df.iloc[:, 0].values
                print(f"   Time: {len(time_array)} points ({time_array[0]:.1f} - {time_array[-1]:.1f} h)")
            
            # Get column names (skip first column which is time)
            # Columns are the actual media names from the experiment
            curve_names = df.columns[1:].tolist()
            print(f"   Curves: {len(curve_names)}")
            
            # Load each curve
            for curve_name in curve_names:
                if max_curves and total_loaded >= max_curves:
                    print(f"   ⚠️  Limit reached ({max_curves})")
                    break
                
                # Get OD values directly by column name
                od_values = df[curve_name].values
                
                # Quality filters:
                # 1. Not all NaN
                # 2. Not all zeros  
                # 3. Shows actual growth (max > min + 0.1)
                # 4. Final OD > 0.2 (actual bacterial growth)
                valid_data = ~np.isnan(od_values)
                if not np.any(valid_data):
                    continue
                
                od_clean = od_values[valid_data]
                od_range = od_clean.max() - od_clean.min()
                
                # Skip flat/no-growth curves
                if od_range < 0.1 or od_clean.max() < 0.2:
                    continue
                
                full_name = f"R{round_num:02d}_{curve_name}"
                all_curves[full_name] = od_values
                total_loaded += 1
            
            print(f"   ✅ Loaded {len([n for n in all_curves if n.startswith(f'R{round_num:02d}')])} curves")
            
            if max_curves and total_loaded >= max_curves:
                break
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Total: {len(all_curves)} curves")
    print(f"{'='*70}")
    
    return {
        'time': time_array,
        'curves': all_curves,
        'metadata': {
            'dataset': 'Aida et al. (2025)',
            'total_curves': len(all_curves)
        }
    }


if __name__ == "__main__":
    print("🥔 TESTING LOADER - CHECKING ALL ROUNDS")
    
    # Load from each round separately to see distribution
    for round_num in [1, 2, 3, 4, 5, 6, 7]:
        print(f"\n{'='*70}")
        print(f"📊 ROUND {round_num}")
        print(f"{'='*70}")
        
        data = load_aida_ecoli_data(data_dir='ecoli_data', max_curves=50, rounds=[round_num])
        
        if len(data['curves']) == 0:
            print("  ⚠️  No valid curves in this round")
            continue
        
        # Show distribution
        max_ods = [np.nanmax(od[~np.isnan(od)]) for od in data['curves'].values() if np.any(~np.isnan(od))]
        
        print(f"  Total curves loaded: {len(max_ods)}")
        print(f"  Max OD range: {min(max_ods):.3f} - {max(max_ods):.3f}")
        print(f"  Mean max OD: {np.mean(max_ods):.3f}")
        
        # Count high-density curves (OD > 1.0)
        high_density = sum(1 for od in max_ods if od > 1.0)
        print(f"  High density curves (>1.0): {high_density}/{len(max_ods)}")
        
        # Show a few examples
        print(f"\n  Sample curves:")
        for name, od in list(data['curves'].items())[:3]:
            valid_od = od[~np.isnan(od)]
            if len(valid_od) > 0:
                print(f"    {name}: {valid_od.min():.3f} → {valid_od.max():.3f}")
    
    print("\n✅ Ready!")
