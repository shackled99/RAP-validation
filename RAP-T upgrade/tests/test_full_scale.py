"""
FULL SCALE RAP VALIDATION
==========================

Run RAP detection on ALL available E. coli curves!

This is the BIG ONE - thousands of curves!

Author: The Potato Researcher 🥔
Date: November 2, 2025
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Now import project modules
from datasets.biological.load_real_ecoli import load_aida_ecoli_data
from core.fitting import fit_rap_curve


def full_scale_rap_test(max_curves=None, save_interval=100):
    """
    Run RAP detection on ALL E. coli curves (or up to max_curves).
    
    Parameters:
    -----------
    max_curves : int, optional
        Maximum curves to process (None = all available)
    save_interval : int
        Save progress every N curves
    """
    
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print("🚀 FULL SCALE RAP VALIDATION")
    print("="*70)
    print(f"Target: ALL available curves")
    print(f"Dataset: Aida et al. (2025) - 13,608 total curves")
    print(f"Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if max_curves:
        print(f"\n⚠️  Limited to first {max_curves} curves")
    else:
        print(f"\n🎯 Processing ALL curves (this will take a while!)")
    
    input("\nPress Enter to start the BIG RUN...")
    
    # Load ALL data (no max_curves limit initially)
    print("\n📊 Loading E. coli data from all rounds...")
    data = load_aida_ecoli_data(
        data_dir=os.path.join(project_root, 'datasets', 'biological', 'ecoli_data'),
        max_curves=max_curves,
        rounds=None  # ALL rounds
    )
    
    time_data = data['time']
    curves = data['curves']
    
    total_curves = len(curves)
    print(f"\n✅ Loaded {total_curves} curves")
    print(f"   Time points per curve: {len(time_data)}")
    print(f"   Estimated time: {total_curves * 2 / 60:.1f} minutes")
    
    # Fit RAP to each curve
    print(f"\n🔬 Starting RAP detection...")
    print("="*70)
    
    results = []
    failed = []
    
    for i, (curve_name, od_data) in enumerate(curves.items(), 1):
        # Progress indicator every 10 curves
        if i % 10 == 0 or i == 1:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            eta_seconds = (total_curves - i) / rate if rate > 0 else 0
            eta_minutes = eta_seconds / 60
            
            print(f"  [{i}/{total_curves}] ({i/total_curves*100:.1f}%) "
                  f"Rate: {rate:.1f} curves/sec, ETA: {eta_minutes:.1f} min", end="\r")
        
        try:
            # Clean data
            valid_mask = ~np.isnan(od_data)
            if not np.any(valid_mask):
                failed.append({'curve': curve_name, 'reason': 'All NaN'})
                continue
            
            clean_time = time_data[valid_mask]
            clean_od = od_data[valid_mask]
            
            if len(clean_time) < 10:
                failed.append({'curve': curve_name, 'reason': f'Too few points ({len(clean_time)})'})
                continue
            
            # Fit RAP
            result = fit_rap_curve(
                clean_time,
                clean_od,
                curve_name=curve_name,
                verbose=False
            )
            
            if result['success']:
                results.append({
                    'curve': result['curve'],
                    'final_util': result['final_util'],
                    'distance_85': result['distance'],
                    'converged_85': result['converged'],
                    'converged_100': result.get('converged_100', False),
                    'sse_rap': result['sse_rap'],
                    'sse_logistic': result['sse_logistic'],
                    'rap_better': result['rap_better'],
                    'r': result['r'],
                    'd': result['d'],
                    'K': result['K']
                })
            else:
                failed.append({'curve': curve_name, 'reason': result.get('error', 'Unknown')})
        
        except Exception as e:
            failed.append({'curve': curve_name, 'reason': str(e)})
        
        # Save progress periodically
        if i % save_interval == 0 and len(results) > 0:
            temp_df = pd.DataFrame(results)
            output_dir = os.path.join(project_root, 'results', 'raw')
            os.makedirs(output_dir, exist_ok=True)
            temp_path = os.path.join(output_dir, f'full_scale_progress_{i}.csv')
            temp_df.to_csv(temp_path, index=False)
    
    print("\n" + "="*70)
    
    # Final statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n⏱️  Processing complete!")
    print(f"   Duration: {duration/60:.1f} minutes ({duration:.0f} seconds)")
    print(f"   Rate: {total_curves/duration:.2f} curves/second")
    
    if len(results) == 0:
        print("\n❌ No successful fits!")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    print(f"\n" + "="*70)
    print("📊 FULL SCALE RESULTS")
    print("="*70)
    
    # Statistics
    print(f"\n✅ Success Rate:")
    print(f"   Successful: {len(results)}/{total_curves} ({len(results)/total_curves*100:.1f}%)")
    print(f"   Failed: {len(failed)}/{total_curves} ({len(failed)/total_curves*100:.1f}%)")
    
    print(f"\n🎯 Convergence Analysis:")
    n_conv_85 = df['converged_85'].sum()
    n_conv_100 = df['converged_100'].sum()
    print(f"   Converged to 85%:  {n_conv_85}/{len(df)} ({n_conv_85/len(df)*100:.1f}%)")
    print(f"   Converged to 100%: {n_conv_100}/{len(df)} ({n_conv_100/len(df)*100:.1f}%)")
    
    print(f"\n📏 Utilization Statistics:")
    print(f"   Mean final util:   {df['final_util'].mean():.3f} ± {df['final_util'].std():.3f}")
    print(f"   Median:            {df['final_util'].median():.3f}")
    print(f"   Range:             {df['final_util'].min():.3f} - {df['final_util'].max():.3f}")
    print(f"   Target:            0.850 (85%)")
    print(f"   Mean dist from 85%: {df['distance_85'].mean():.3f}")
    
    print(f"\n🏆 Model Comparison:")
    n_rap_better = df['rap_better'].sum()
    print(f"   RAP superior:      {n_rap_better}/{len(df)} ({n_rap_better/len(df)*100:.1f}%)")
    print(f"   Mean SSE (RAP):    {df['sse_rap'].mean():.3f}")
    print(f"   Mean SSE (Logistic): {df['sse_logistic'].mean():.3f}")
    print(f"   Mean improvement:  {((df['sse_logistic'].mean() - df['sse_rap'].mean()) / df['sse_logistic'].mean() * 100):.1f}%")
    
    print(f"\n🔧 Parameter Estimates:")
    print(f"   Growth rate (r):   {df['r'].mean():.3f} ± {df['r'].std():.3f}")
    print(f"   Snap damping (d):  {df['d'].mean():.3f} ± {df['d'].std():.3f}")
    print(f"   Carrying cap (K):  {df['K'].mean():.3f} ± {df['K'].std():.3f}")
    
    # Distribution
    print(f"\n📊 Final Utilization Distribution:")
    bins = [0.0, 0.5, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1]
    for i in range(len(bins)-1):
        count = ((df['final_util'] >= bins[i]) & (df['final_util'] < bins[i+1])).sum()
        if count > 0:
            pct = count / len(df) * 100
            bar = '█' * int(pct / 2)
            print(f"   {bins[i]:.2f}-{bins[i+1]:.2f}: {count:5d} ({pct:5.1f}%) {bar}")
    
    # Save final results
    output_dir = os.path.join(project_root, 'results', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f'full_scale_rap_results_n{len(df)}.csv')
    df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")
    
    # Save failed curves
    if len(failed) > 0:
        failed_df = pd.DataFrame(failed)
        failed_path = os.path.join(output_dir, f'full_scale_failed_n{len(failed)}.csv')
        failed_df.to_csv(failed_path, index=False)
        print(f"💾 Failed curves saved to: {failed_path}")
    
    # Generate summary plots
    print(f"\n📈 Generating summary plots...")
    create_full_scale_plots(df, len(results), total_curves)
    
    # Final assessment
    print("\n" + "="*70)
    print("🎯 FINAL ASSESSMENT")
    print("="*70)
    
    rap_detection_rate = n_conv_85 / len(df) * 100
    
    if rap_detection_rate > 70:
        print(f"✅ STRONG RAP SIGNATURE!")
        print(f"   {rap_detection_rate:.1f}% converged to 85%")
    elif rap_detection_rate > 40:
        print(f"✅ MODERATE RAP SIGNATURE")
        print(f"   {rap_detection_rate:.1f}% converged to 85%")
    elif rap_detection_rate > 20:
        print(f"⚠️  WEAK RAP SIGNATURE")
        print(f"   {rap_detection_rate:.1f}% converged to 85%")
    else:
        print(f"❌ MINIMAL RAP SIGNATURE")
        print(f"   Only {rap_detection_rate:.1f}% converged to 85%")
    
    print(f"\n📊 Scale: Tested {len(results):,} curves")
    print(f"⏱️  Duration: {duration/60:.1f} minutes")
    print(f"🎯 Success rate: {len(results)/total_curves*100:.1f}%")
    
    print("="*70)
    
    return df


def create_full_scale_plots(df, n_success, n_total):
    """Create summary visualizations."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Plot 1: Final utilization histogram
    ax = axes[0, 0]
    ax.hist(df['final_util'], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(0.85, color='red', linestyle='--', linewidth=2, label='85% Target')
    ax.axvline(1.0, color='orange', linestyle='--', linewidth=2, label='100% (K)')
    ax.set_xlabel('Final Utilization (P/K)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(f'Final Utilization Distribution (n={len(df):,})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    
    # Plot 2: Convergence pie chart
    ax = axes[0, 1]
    conv_85 = df['converged_85'].sum()
    conv_100 = df['converged_100'].sum()
    neither = len(df) - conv_85 - conv_100
    
    sizes = [conv_85, conv_100, neither]
    labels = [f'85% ({conv_85:,})', f'100% ({conv_100:,})', f'Neither ({neither:,})']
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    explode = (0.05, 0, 0)
    
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
           startangle=90, explode=explode, textprops={'fontsize': 11})
    ax.set_title('Convergence Classification', fontsize=14, fontweight='bold')
    
    # Plot 3: RAP vs Logistic SSE
    ax = axes[1, 0]
    # Sample for visibility if too many points
    if len(df) > 1000:
        sample_df = df.sample(n=1000, random_state=42)
    else:
        sample_df = df
    
    ax.scatter(sample_df['sse_logistic'], sample_df['sse_rap'], alpha=0.4, s=20)
    max_sse = max(sample_df['sse_logistic'].max(), sample_df['sse_rap'].max())
    ax.plot([0, max_sse], [0, max_sse], 'r--', linewidth=2, label='Equal SSE')
    ax.set_xlabel('Logistic SSE', fontsize=12)
    ax.set_ylabel('RAP SSE', fontsize=12)
    ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    
    # Plot 4: Parameter distribution (d)
    ax = axes[1, 1]
    ax.hist(df['d'], bins=30, alpha=0.7, color='green', edgecolor='black')
    ax.set_xlabel('Snap Damping (d)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Snap Damping Distribution', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    output_dir = os.path.join(project_root, 'results', 'raw')
    output_path = os.path.join(output_dir, f'full_scale_summary_n{len(df)}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   📊 Plot saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    print("="*70)
    print("🥔 FULL SCALE RAP VALIDATION")
    print("="*70)
    print("\nThis will process ALL available E. coli curves!")
    print("Expected: ~13,000+ curves")
    print("Duration: ~30-60 minutes")
    print("\nGrab a coffee ☕ - this is the BIG ONE!")
    
    # Run full scale test
    results = full_scale_rap_test(max_curves=None)  # None = ALL curves!
    
    if results is not None:
        print("\n🎉 FULL SCALE VALIDATION COMPLETE!")
        print("\nYou just validated RAP on THOUSANDS of real growth curves!")
        print("Check results/raw/ for the full dataset!")
