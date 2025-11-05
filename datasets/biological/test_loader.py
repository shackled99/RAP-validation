"""
Real E. coli Data Loader - Aida et al. (2025)
==============================================

Quick test script to verify the loader works.
Run this from the datasets/biological directory.

Author: The Potato Researcher 🥔
"""

import sys
sys.path.insert(0, '../..')

from datasets.biological.load_real_ecoli import load_aida_ecoli_data

if __name__ == "__main__":
    print("="*70)
    print("🥔 TESTING REAL E. COLI DATA LOADER")
    print("="*70)
    
    # Load 5 curves as a test
    data = load_aida_ecoli_data(data_dir='ecoli_data', max_curves=5)
    
    print(f"\n📊 Loaded Data Summary:")
    print(f"  Curves: {len(data['curves'])}")
    print(f"  Time points: {len(data['time'])}")
    print(f"  Time range: {data['time'][0]:.1f} - {data['time'][-1]:.1f} hours")
    
    print(f"\n🔬 Sample curves:")
    for i, (name, od_values) in enumerate(list(data['curves'].items())[:5], 1):
        print(f"  {i}. {name}")
        print(f"     OD range: {od_values.min():.3f} - {od_values.max():.3f}")
        print(f"     Final OD: {od_values[-1]:.3f}")
    
    print("\n✅ Loader working correctly!")
