"""
Real E. coli RAP Test
=====================

Test RAP detection on REAL E. coli growth data from Aida et al. (2025)

This is THE BIG TEST - real biological data validation!

Author: The Potato Researcher 🥔
Date: November 2025
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Now import project modules
from datasets.biological.load_real_ecoli import load_aida_ecoli_data
from core.fitting import fit_rap_curve


def test_real_ecoli_rap(n_curves=50, rounds=[5]):
    """
    Run RAP detection on real E. coli data.
    
    Parameters:
    -----------
    n_curves : int
        Number of curves to test
    rounds : list
        Which rounds to load (default: [5] - best data)
    """
    
    print("\n" + "="*70)
    print("🔬 RAP DETECTION ON REAL E. COLI DATA")
    print("="*70)
    print(f"Dataset: Aida et al. (2025)")
    print(f"Organism: E. coli BW25113")
    print(f"Rounds: {rounds}")
    print(f"Target curves: {n_curves}")
    print("="*70)
    
    input("\nPress Enter to start...")
    
    # Load real data
    print("\n📊 Loading real E. coli data...")
    
    # Path to data from tests directory
    data_dir = os.path.join(project_root, 'datasets', 'biological', 'ecoli_data')
    
    data = load_aida_ecoli_data(
        data_dir=data_dir,
        max_curves=n_curves,
        rounds=rounds
    )
    
    time_data = data['time']
    curves = data['curves']
    
    print(f"\n✅ Loaded {len(curves)} real growth curves")
    print(f"   Time points: {len(time_data)}")
    print(f"   Time range: {time_data[0]:.1f} - {time_data[-1]:.1f} hours")
    
    # Fit RAP to each curve
    print(f"\n🔬 Running RAP detection on {len(curves)} curves...")
    print("="*70)
    
    results = []
    
    for i, (curve_name, od_data) in enumerate(curves.items(), 1):
        print(f"  [{i}/{len(curves)}] {curve_name}...", end=" ")
        
        try:
            # Clean data: remove NaN values
            valid_mask = ~np.isnan(od_data)
            if not np.any(valid_mask):
                print("❌ All NaN")
                continue
            
            # Get valid time and OD points
            clean_time = time_data[valid_mask]
            clean_od = od_data[valid_mask]
            
            # Need at least 10 points for fitting
            if len(clean_time) < 10:
                print(f"❌ Too few points ({len(clean_time)})")
                continue
            
            result = fit_rap_curve(
                clean_time,
                clean_od,
                curve_name=curve_name,
                verbose=False  # Quiet mode for batch
            )
            
            if result['success']:
                print("✅")
                results.append(result)
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Analyze results
    print("\n" + "="*70)
    print("📊 REAL E. COLI RESULTS")
    print("="*70)
    
    if len(results) == 0:
        print("❌ No successful fits!")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'curve': r['curve'],
            'final_util': r['final_util'],
            'distance_85': r['distance'],
            'converged_85': r['converged'],
            'converged_100': r.get('converged_100', False),
            'sse_rap': r['sse_rap'],
            'sse_logistic': r['sse_logistic'],
            'rap_better': r['rap_better'],
            'r': r['r'],
            'd': r['d'],
            'K': r['K']
        }
        for r in results
    ])
    
    # Statistics
    print(f"\n✅ Success Rate:")
    print(f"   Fits succeeded: {len(results)}/{len(curves)} ({len(results)/len(curves)*100:.1f}%)")
    
    print(f"\n🎯 Convergence Analysis:")
    n_conv_85 = df['converged_85'].sum()
    n_conv_100 = df['converged_100'].sum()
    print(f"   Converged to 85%:  {n_conv_85}/{len(df)} ({n_conv_85/len(df)*100:.1f}%)")
    print(f"   Converged to 100%: {n_conv_100}/{len(df)} ({n_conv_100/len(df)*100:.1f}%)")
    
    print(f"\n📏 Utilization Statistics:")
    print(f"   Mean final util:   {df['final_util'].mean():.3f} ± {df['final_util'].std():.3f}")
    print(f"   Range:             {df['final_util'].min():.3f} - {df['final_util'].max():.3f}")
    print(f"   Target:            0.850 (85%)")
    print(f"   Mean dist from 85%: {df['distance_85'].mean():.3f}")
    
    print(f"\n🏆 Model Comparison:")
    n_rap_better = df['rap_better'].sum()
    print(f"   RAP superior:      {n_rap_better}/{len(df)} ({n_rap_better/len(df)*100:.1f}%)")
    print(f"   Mean SSE (RAP):    {df['sse_rap'].mean():.3f}")
    print(f"   Mean SSE (Logistic): {df['sse_logistic'].mean():.3f}")
    
    print(f"\n🔧 Parameter Estimates:")
    print(f"   Growth rate (r):   {df['r'].mean():.3f} ± {df['r'].std():.3f}")
    print(f"   Snap damping (d):  {df['d'].mean():.3f} ± {df['d'].std():.3f}")
    print(f"   Carrying cap (K):  {df['K'].mean():.3f} ± {df['K'].std():.3f}")
    
    # Show distribution
    print(f"\n📊 Final Utilization Distribution:")
    bins = [0.0, 0.5, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1]
    for i in range(len(bins)-1):
        count = ((df['final_util'] >= bins[i]) & (df['final_util'] < bins[i+1])).sum()
        if count > 0:
            bar = '█' * int(count / len(df) * 50)
            print(f"   {bins[i]:.2f}-{bins[i+1]:.2f}: {count:3d} {bar}")
    
    # Save results
    output_dir = os.path.join(project_root, 'results', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'real_ecoli_rap_results.csv')
    df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    # Create summary plot
    print(f"\n📈 Generating summary plot...")
    create_summary_plot(df, rounds)
    
    # Final assessment
    print("\n" + "="*70)
    print("🎯 ASSESSMENT")
    print("="*70)
    
    rap_detection_rate = n_conv_85 / len(df) * 100
    
    if rap_detection_rate > 50:
        print(f"✅ STRONG RAP SIGNATURE DETECTED!")
        print(f"   {rap_detection_rate:.1f}% of curves converged to 85% attractor")
    elif rap_detection_rate > 20:
        print(f"⚠️  MODERATE RAP SIGNATURE")
        print(f"   {rap_detection_rate:.1f}% of curves show 85% convergence")
    else:
        print(f"❌ WEAK RAP SIGNATURE")
        print(f"   Only {rap_detection_rate:.1f}% converged to 85%")
    
    if n_conv_100 > n_conv_85:
        print(f"\n⚠️  NOTE: More curves converged to 100% ({n_conv_100}) than 85% ({n_conv_85})")
        print(f"   This suggests logistic-like behavior in real data")
    
    if n_rap_better / len(df) > 0.7:
        print(f"\n✅ RAP MODEL SUPERIOR!")
        print(f"   RAP fits better than Logistic in {n_rap_better/len(df)*100:.1f}% of cases")
    
    print("="*70)
    
    return df


def create_summary_plot(df, rounds):
    """Create summary visualization of results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Final utilization distribution
    ax = axes[0, 0]
    ax.hist(df['final_util'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(0.85, color='red', linestyle='--', linewidth=2, label='85% Attractor')
    ax.axvline(1.0, color='orange', linestyle='--', linewidth=2, label='100% (K)')
    ax.set_xlabel('Final Utilization (P/K)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Final Utilization - Real E. coli')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Plot 2: RAP vs Logistic SSE
    ax = axes[0, 1]
    ax.scatter(df['sse_logistic'], df['sse_rap'], alpha=0.6, s=50)
    max_sse = max(df['sse_logistic'].max(), df['sse_rap'].max())
    ax.plot([0, max_sse], [0, max_sse], 'r--', label='Equal SSE')
    ax.set_xlabel('Logistic SSE')
    ax.set_ylabel('RAP SSE')
    ax.set_title('Model Comparison: RAP vs Logistic')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Plot 3: Parameter distributions
    ax = axes[1, 0]
    ax.hist(df['d'], bins=15, alpha=0.7, color='green', edgecolor='black')
    ax.set_xlabel('Snap Damping (d)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Snap Damping Parameter')
    ax.grid(alpha=0.3)
    
    # Plot 4: Convergence pie chart
    ax = axes[1, 1]
    conv_85 = df['converged_85'].sum()
    conv_100 = df['converged_100'].sum()
    neither = len(df) - conv_85 - conv_100
    
    sizes = [conv_85, conv_100, neither]
    labels = [f'85% ({conv_85})', f'100% ({conv_100})', f'Neither ({neither})']
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.set_title('Convergence Classification')
    
    plt.tight_layout()
    
    output_dir = os.path.join(project_root, 'results', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f'real_ecoli_round{rounds[0]}_summary.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"   📊 Plot saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    print("="*70)
    print("🥔 REAL E. COLI RAP VALIDATION")
    print("="*70)
    print("\nThis will test RAP on REAL biological data!")
    print("Using Round 5 (best quality, high-density growth)")
    
    # Run test on Round 5 (best data)
    results = test_real_ecoli_rap(n_curves=50, rounds=[5])
    
    if results is not None:
        print("\n🎉 Real data validation complete!")
        print("\nCheck results/raw/ for:")
        print("  - real_ecoli_rap_results.csv")
        print("  - real_ecoli_round5_summary.png")
