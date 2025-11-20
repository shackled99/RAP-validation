"""
RAP Validation Test - With TRUE RAP Data
=========================================

Tests RAP detection using data generated WITH actual RAP dynamics.

This should show 85% convergence!

Author: The Potato Researcher 🥔
Date: November 2025
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from generate_rap_test_data import generate_rap_test_data
from core.fitting import fit_rap_curve, batch_fit_curves
from core.visualization import plot_rap_fit, plot_batch_summary


def test_rap_detection():
    """
    Test RAP detection on data with TRUE RAP dynamics.
    """
    
    print("\n" + "="*70)
    print("🧬 RAP DETECTION TEST - TRUE RAP DYNAMICS")
    print("="*70)
    print("\nThis test uses data generated WITH actual RAP dynamics.")
    print("We should see convergence to 85% attractor!\n")
    
    input("Press Enter to start...")
    
    # Generate test data with TRUE RAP dynamics
    rap_data = generate_rap_test_data(n_curves=10, n_points=100, time_max=40)
    
    # Create DataFrame
    df_data = {'Time (h)': rap_data['time']}
    df_data.update(rap_data['curves'])
    df = pd.DataFrame(df_data)
    
    # Get curve names
    curve_names = list(rap_data['curves'].keys())
    
    print(f"\n" + "="*70)
    print(f"🔬 FITTING RAP MODEL TO RAP-GENERATED DATA")
    print(f"="*70)
    
    # Batch fit
    results_df = batch_fit_curves(
        rap_data['time'],
        df,
        od_columns=curve_names,
        verbose=False
    )
    
    # Save results
    results_path = '../results/raw/rap_validation_results.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\n💾 Results saved to: {results_path}")
    
    # Analyze results
    successful = results_df[results_df['success'] == True]
    
    if len(successful) > 0:
        print(f"\n" + "="*70)
        print(f"📊 RAP DETECTION RESULTS")
        print(f"="*70)
        
        print(f"\n✅ Success Rate:")
        print(f"   Fits succeeded: {len(successful)}/{len(results_df)} ({len(successful)/len(results_df)*100:.0f}%)")
        
        print(f"\n🎯 Convergence Analysis:")
        converged = successful['converged'].sum()
        print(f"   Converged to 85%: {converged}/{len(successful)} ({successful['converged'].mean()*100:.1f}%)")
        print(f"   Expected:         {rap_data['expected_convergence']}/{len(successful)}")
        
        print(f"\n📏 Utilization Statistics:")
        print(f"   Mean final util:  {successful['final_util'].mean():.3f} ± {successful['final_util'].std():.3f}")
        print(f"   Target:           0.850 (85%)")
        print(f"   Mean distance:    {successful['distance'].mean():.3f}")
        
        print(f"\n🏆 Model Comparison:")
        rap_wins = successful['rap_better'].sum()
        print(f"   RAP superior:     {rap_wins}/{len(successful)} ({successful['rap_better'].mean()*100:.1f}%)")
        print(f"   Mean SSE (RAP):   {successful['sse_rap'].mean():.3f}")
        print(f"   Mean SSE (Log):   {successful['sse_logistic'].mean():.3f}")
        
        # Detailed comparison
        print(f"\n📋 Individual Results:")
        print(f"{'Curve':<25} {'Final Util':<12} {'Distance':<10} {'Converged':<12} {'RAP Better'}")
        print("-"*70)
        for _, row in successful.iterrows():
            converge_mark = '✅' if row['converged'] else '❌'
            rap_mark = '✅' if row['rap_better'] else '❌'
            print(f"{row['curve']:<25} {row['final_util']:<12.3f} {row['distance']:<10.3f} {converge_mark:<12} {rap_mark}")
        
        # Generate plots
        print(f"\n📈 Generating summary plots...")
        plot_batch_summary(
            results_df,
            show_plot=True,
            save_path='../results/raw/rap_validation_summary.png'
        )
        
        # Final verdict
        print(f"\n" + "="*70)
        if successful['converged'].mean() > 0.7:  # >70% convergence
            print(f"🎉 RAP DETECTION SUCCESSFUL!")
            print(f"   The 85% attractor is REAL and DETECTABLE!")
            print(f"   System correctly identifies RAP dynamics!")
        elif successful['converged'].mean() > 0.3:  # 30-70%
            print(f"⚠️  PARTIAL RAP DETECTION")
            print(f"   Some curves show 85% convergence")
            print(f"   May need parameter tuning")
        else:
            print(f"❌ RAP DETECTION WEAK")
            print(f"   85% convergence not consistently detected")
            print(f"   Check parameter bounds and fitting strategy")
        print(f"="*70)
    
    else:
        print(f"\n❌ All fits failed!")
    
    return results_df


if __name__ == "__main__":
    results = test_rap_detection()
