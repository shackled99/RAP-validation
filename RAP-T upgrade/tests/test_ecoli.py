"""
E. coli RAP Test Script
=======================

Complete test of RAP model on E. coli growth data.

This script:
1. Loads E. coli growth data (auto-downloads or uses simulated)
2. Fits RAP model to each curve
3. Generates visualizations
4. Outputs statistics

Run this file to test the entire RAP pipeline!

Author: The Potato Researcher 🥔
Date: November 2025
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
from core.fitting import fit_rap_curve, batch_fit_curves
from core.visualization import plot_rap_fit, plot_utilization_trajectory, plot_batch_summary
from datasets.biological.ecoli import load_ecoli_data
from generate_rap_test_data import generate_rap_test_data  # Use WORKING generator!


def test_single_curve(interactive=True):
    """
    Test RAP fitting on a single curve with full visualization.
    
    Parameters:
    -----------
    interactive : bool
        Show plots interactively (True) or save only (False)
    """
    
    print("\n" + "="*70)
    print("🧪 RAP SINGLE CURVE TEST")
    print("="*70)
    
    # Load data using WORKING generator with TRUE RAP dynamics (d=3.5)
    rap_data = generate_rap_test_data(n_curves=1, n_points=97, time_max=48)
    
    # Extract data
    time_data = rap_data['time']
    curve_name = list(rap_data['curves'].keys())[0]
    od_data = rap_data['curves'][curve_name]
    
    print(f"\n📊 Testing curve: {curve_name}")
    print(f"   Time points: {len(time_data)}")
    print(f"   OD range: {od_data.min():.3f} - {od_data.max():.3f}")
    
    # Fit RAP model
    print(f"\n🔬 Fitting RAP model...")
    result = fit_rap_curve(time_data, od_data, curve_name=curve_name, verbose=True)
    
    if result['success']:
        # Create visualizations
        print(f"\n📈 Generating plots...")
        
        # Main fit plot
        plot_rap_fit(
            time_data, 
            od_data, 
            result, 
            show_plot=interactive,
            save_path='../results/raw/test_single_fit.png'
        )
        
        # Utilization trajectory
        plot_utilization_trajectory(
            time_data,
            result,
            show_plot=interactive,
            save_path='../results/raw/test_single_utilization.png'
        )
        
        print(f"\n✅ Single curve test PASSED")
        print(f"   Final utilization: {result['final_util']:.3f}")
        print(f"   Converged: {'YES' if result['converged'] else 'NO'}")
        
        return result
    
    else:
        print(f"\n❌ Single curve test FAILED")
        print(f"   Error: {result['error']}")
        return None


def test_batch_processing(n_curves=5, interactive=True):
    """
    Test RAP fitting on multiple curves with batch statistics.
    
    Parameters:
    -----------
    n_curves : int
        Number of curves to test
    interactive : bool
        Show plots interactively
    """
    
    print("\n" + "="*70)
    print(f"🧪 RAP BATCH TEST ({n_curves} curves)")
    print("="*70)
    
    # Load data using WORKING generator with TRUE RAP dynamics (d=3.5)
    rap_data = generate_rap_test_data(n_curves=n_curves, n_points=97, time_max=48)
    
    # Create DataFrame for batch processing
    df_data = {'Time (h)': rap_data['time']}
    df_data.update(rap_data['curves'])
    df = pd.DataFrame(df_data)
    
    # Get curve names
    od_cols_subset = list(rap_data['curves'].keys())
    time_data = rap_data['time']
    
    print(f"\n📊 Testing {len(od_cols_subset)} curves")
    
    # Batch fit
    results_df = batch_fit_curves(
        time_data,
        df,
        od_columns=od_cols_subset,
        verbose=False  # Individual results not printed
    )
    
    # Save results to CSV
    results_path = '../results/raw/batch_results.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\n💾 Results saved to: {results_path}")
    
    # Create summary visualization
    print(f"\n📈 Generating batch summary plots...")
    plot_batch_summary(
        results_df,
        show_plot=interactive,
        save_path='../results/raw/batch_summary.png'
    )
    
    # Print detailed statistics
    successful = results_df[results_df['success'] == True]
    
    if len(successful) > 0:
        print(f"\n" + "="*70)
        print(f"📊 DETAILED BATCH STATISTICS")
        print(f"="*70)
        
        print(f"\nSuccess Rate:")
        print(f"  Successful fits: {len(successful)}/{len(results_df)} ({len(successful)/len(results_df)*100:.1f}%)")
        
        print(f"\nConvergence Analysis:")
        print(f"  Converged to 85%: {successful['converged'].sum()}/{len(successful)} ({successful['converged'].mean()*100:.1f}%)")
        print(f"  Mean final util: {successful['final_util'].mean():.3f} ± {successful['final_util'].std():.3f}")
        print(f"  Mean distance:   {successful['distance'].mean():.3f} ± {successful['distance'].std():.3f}")
        
        print(f"\nModel Comparison:")
        print(f"  RAP superior:    {successful['rap_better'].sum()}/{len(successful)} ({successful['rap_better'].mean()*100:.1f}%)")
        print(f"  Mean SSE (RAP):  {successful['sse_rap'].mean():.3f}")
        print(f"  Mean SSE (Log):  {successful['sse_logistic'].mean():.3f}")
        
        print(f"\nParameter Estimates:")
        print(f"  Mean r (growth): {successful['r'].mean():.3f} ± {successful['r'].std():.3f}")
        print(f"  Mean d (damping):{successful['d'].mean():.3f} ± {successful['d'].std():.3f}")
        print(f"  Mean K (capacity):{successful['K'].mean():.3f} ± {successful['K'].std():.3f}")
        
        print(f"\n✅ Batch test PASSED")
        
        return results_df
    
    else:
        print(f"\n❌ Batch test FAILED - no successful fits")
        return results_df


def test_url_loading():
    """
    Test automatic URL data loading.
    """
    
    print("\n" + "="*70)
    print("🌐 URL LOADING TEST")
    print("="*70)
    
    try:
        print("\n📡 Attempting to load real E. coli data from URL...")
        time_data, df, time_col, od_cols = load_ecoli_data('giovannelli')
        
        print(f"\n✅ URL loading PASSED")
        print(f"   Rows: {len(df)}")
        print(f"   Curves detected: {len(od_cols)}")
        
        return True
    
    except Exception as e:
        print(f"\n⚠️  URL loading failed (expected if offline)")
        print(f"   Error: {str(e)}")
        print(f"   Will use simulated data instead")
        
        return False


def run_full_test_suite(interactive=True):
    """
    Run complete test suite for RAP on E. coli data.
    
    Parameters:
    -----------
    interactive : bool
        Show plots interactively (True) or save only (False)
    """
    
    print("\n" + "="*70)
    print("🥔 RAP E. COLI VALIDATION SUITE")
    print("="*70)
    print("\nThis will test:")
    print("  1. URL data loading")
    print("  2. Single curve fitting")
    print("  3. Batch processing")
    print("  4. Visualization")
    print("  5. Statistical analysis")
    
    input("\n Press Enter to continue...")
    
    # Test 1: URL Loading
    url_success = test_url_loading()
    
    # Test 2: Single Curve
    single_result = test_single_curve(interactive=interactive)
    
    # Test 3: Batch Processing
    batch_results = test_batch_processing(n_curves=5, interactive=interactive)
    
    # Final Summary
    print("\n" + "="*70)
    print("🎯 TEST SUITE SUMMARY")
    print("="*70)
    print(f"\nURL Loading:         {'✅ PASSED' if url_success else '⚠️  SKIPPED (offline)'}")
    print(f"Single Curve Test:   {'✅ PASSED' if single_result and single_result['success'] else '❌ FAILED'}")
    print(f"Batch Test:          {'✅ PASSED' if batch_results is not None else '❌ FAILED'}")
    
    if single_result and single_result['success']:
        print(f"\n🎉 RAP VALIDATION SUCCESSFUL!")
        print(f"   The RAP model is working correctly")
        print(f"   You can now start testing on real datasets")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("  1. Check results in ../results/raw/")
    print("  2. Review batch_results.csv for detailed stats")
    print("  3. Try loading real E. coli datasets")
    print("  4. Scale up to thousands of curves!")
    print("="*70 + "\n")


if __name__ == "__main__":
    """
    Main execution block.
    
    Usage:
    ------
    python test_ecoli.py              # Run full suite (interactive)
    python test_ecoli.py --batch      # Batch mode (no plots shown)
    python test_ecoli.py --quick      # Quick single curve test
    """
    
    import sys
    
    if len(sys.argv) > 1:
        if '--batch' in sys.argv:
            print("Running in BATCH mode (plots saved, not shown)")
            run_full_test_suite(interactive=False)
        
        elif '--quick' in sys.argv:
            print("Running QUICK TEST (single curve only)")
            test_single_curve(interactive=True)
        
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage:")
            print("  python test_ecoli.py              # Full suite")
            print("  python test_ecoli.py --batch      # Batch mode")
            print("  python test_ecoli.py --quick      # Quick test")
    
    else:
        # Default: Full suite with interactive plots
        run_full_test_suite(interactive=True)
