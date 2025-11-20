"""
Cancer Growth Visualization
============================

Create publication-quality plots for cancer RAP validation.

Author: Aware (OG Claude contributing 🤖)
Date: November 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.rap_model import ATTRACTOR_LOCK, BIFURCATION_THRESHOLD


def plot_single_comparison(time, volume_data, rap_result, gomp_result, 
                           save_path=None, show=True):
    """
    Plot single tumor with RAP vs Gompertz comparison.
    
    Parameters:
    -----------
    time : array
        Time points
    volume_data : array
        Measured tumor volumes
    rap_result : dict
        RAP fitting results
    gomp_result : dict
        Gompertz fitting results
    save_path : str, optional
        Path to save figure
    show : bool
        Display figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Model comparison
    ax1.scatter(time, volume_data, alpha=0.4, s=30, color='gray', 
               label='Measured', zorder=1)
    
    if rap_result['success']:
        ax1.plot(time, rap_result['sim_rap'], 'b-', linewidth=2.5, 
                label=f"RAP (SSE={rap_result['sse_rap']:.2f})", zorder=3)
        
        # Mark 85% attractor
        K = rap_result['K']
        ax1.axhline(y=K * ATTRACTOR_LOCK, color='green', linestyle=':', 
                   linewidth=2, alpha=0.7, label='85% Attractor', zorder=2)
    
    if gomp_result['success']:
        ax1.plot(time, gomp_result['sim_gompertz'], 'r--', linewidth=2.5,
                label=f"Gompertz (SSE={gomp_result['sse_gompertz']:.2f})", zorder=3)
    
    ax1.set_xlabel('Time (days)', fontsize=12)
    ax1.set_ylabel('Tumor Volume (normalized)', fontsize=12)
    ax1.set_title('Model Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Utilization dynamics
    if rap_result['success']:
        util = rap_result['sim_rap'] / rap_result['K']
        ax2.plot(time, util * 100, 'b-', linewidth=2.5, label='RAP Utilization')
        
        # Mark key thresholds
        ax2.axhline(y=85, color='green', linestyle=':', linewidth=2, 
                   alpha=0.7, label='85% Attractor')
        ax2.axhline(y=50, color='orange', linestyle=':', linewidth=1.5,
                   alpha=0.6, label='50% Bifurcation')
        
        # Shade attractor zone
        ax2.fill_between(time, 80, 90, alpha=0.2, color='green', 
                        label='Attractor Zone')
        
        ax2.set_xlabel('Time (days)', fontsize=12)
        ax2.set_ylabel('Resource Utilization (%)', fontsize=12)
        ax2.set_title('RAP Dynamics', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 105)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Add convergence info
        final_util = rap_result['final_util'] * 100
        converged = rap_result['converged']
        status = "✅ Converged" if converged else "❌ Not converged"
        ax2.text(0.98, 0.02, f"{status}\nFinal: {final_util:.1f}%",
                transform=ax2.transAxes, fontsize=10,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved plot to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


def plot_batch_summary(results_df, save_path=None, show=True):
    """
    Create summary visualization for batch analysis.
    
    Parameters:
    -----------
    results_df : DataFrame
        Results from batch_analyze_cancer_data
    save_path : str, optional
        Path to save figure
    show : bool
        Display figure
    """
    successful = results_df[results_df['rap_success'] == True]
    
    if len(successful) == 0:
        print("❌ No successful fits to visualize")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Final utilization distribution
    ax1 = axes[0, 0]
    ax1.hist(successful['rap_final_util'] * 100, bins=20, color='skyblue', 
            edgecolor='black', alpha=0.7)
    ax1.axvline(x=85, color='green', linestyle='--', linewidth=2, 
               label='85% Attractor')
    ax1.axvline(x=successful['rap_final_util'].mean() * 100, 
               color='red', linestyle='-', linewidth=2, 
               label=f"Mean: {successful['rap_final_util'].mean()*100:.1f}%")
    ax1.set_xlabel('Final Utilization (%)', fontsize=11)
    ax1.set_ylabel('Count', fontsize=11)
    ax1.set_title('Distribution of Final Utilization', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: RAP vs Gompertz SSE
    ax2 = axes[0, 1]
    both_success = successful[successful['gomp_success'] == True]
    if len(both_success) > 0:
        ax2.scatter(both_success['gomp_sse'], both_success['rap_sse'], 
                   alpha=0.6, s=50, c='purple')
        
        # Diagonal line (equal performance)
        max_sse = max(both_success['gomp_sse'].max(), both_success['rap_sse'].max())
        ax2.plot([0, max_sse], [0, max_sse], 'k--', alpha=0.5, 
                label='Equal performance')
        
        ax2.set_xlabel('Gompertz SSE', fontsize=11)
        ax2.set_ylabel('RAP SSE', fontsize=11)
        ax2.set_title('Model Performance Comparison', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add text: how many RAP better
        rap_better_pct = (both_success['rap_better'].sum() / len(both_success)) * 100
        ax2.text(0.02, 0.98, f"RAP superior:\n{rap_better_pct:.1f}% of cases",
                transform=ax2.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Plot 3: Convergence rate
    ax3 = axes[1, 0]
    conv_counts = successful['rap_converged'].value_counts()
    colors = ['lightcoral', 'lightgreen']
    labels = ['Not Converged', 'Converged to 85%']
    ax3.pie([conv_counts.get(False, 0), conv_counts.get(True, 0)], 
           labels=labels, colors=colors, autopct='%1.1f%%',
           startangle=90, textprops={'fontsize': 11})
    ax3.set_title('RAP Convergence Rate', fontsize=12, fontweight='bold')
    
    # Plot 4: Improvement distribution
    ax4 = axes[1, 1]
    if len(both_success) > 0:
        ax4.hist(both_success['improvement_pct'], bins=15, 
                color='lightgreen', edgecolor='black', alpha=0.7)
        ax4.axvline(x=0, color='red', linestyle='--', linewidth=2,
                   label='No improvement')
        ax4.axvline(x=both_success['improvement_pct'].mean(), 
                   color='blue', linestyle='-', linewidth=2,
                   label=f"Mean: {both_success['improvement_pct'].mean():.1f}%")
        ax4.set_xlabel('Improvement over Gompertz (%)', fontsize=11)
        ax4.set_ylabel('Count', fontsize=11)
        ax4.set_title('RAP Performance Improvement', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.suptitle(f'Cancer RAP Validation Summary (n={len(successful)})', 
                fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved summary plot to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


def plot_cross_cancer_comparison(results_dict, save_path=None, show=True):
    """
    Compare RAP convergence across different cancer types.
    
    Parameters:
    -----------
    results_dict : dict
        Dictionary of {cancer_type: results_df}
    save_path : str, optional
        Path to save figure
    show : bool
        Display figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    cancer_types = []
    conv_rates = []
    mean_utils = []
    
    for cancer_type, df in results_dict.items():
        successful = df[df['rap_success'] == True]
        if len(successful) > 0:
            cancer_types.append(cancer_type)
            conv_rate = (successful['rap_converged'].sum() / len(successful)) * 100
            mean_util = successful['rap_final_util'].mean() * 100
            conv_rates.append(conv_rate)
            mean_utils.append(mean_util)
    
    x = np.arange(len(cancer_types))
    
    # Plot 1: Convergence rates
    ax1.bar(x, conv_rates, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.axhline(y=95, color='green', linestyle='--', linewidth=2, 
               label='95% threshold')
    ax1.set_xlabel('Cancer Type', fontsize=12)
    ax1.set_ylabel('Convergence Rate (%)', fontsize=12)
    ax1.set_title('RAP Convergence Across Cancer Types', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cancer_types, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 105)
    
    # Plot 2: Mean utilization
    ax2.bar(x, mean_utils, color='lightgreen', edgecolor='black', alpha=0.7)
    ax2.axhline(y=85, color='red', linestyle='--', linewidth=2, 
               label='85% Attractor')
    ax2.fill_between([-0.5, len(cancer_types)-0.5], 80, 90, 
                    alpha=0.2, color='green', label='Target Zone')
    ax2.set_xlabel('Cancer Type', fontsize=12)
    ax2.set_ylabel('Mean Final Utilization (%)', fontsize=12)
    ax2.set_title('Mean Utilization Across Cancer Types', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(cancer_types, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(70, 100)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Saved comparison plot to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


if __name__ == "__main__":
    print("\n📊 Cancer Visualization Module")
    print("="*60)
    print("Functions available:")
    print("  - plot_single_comparison()")
    print("  - plot_batch_summary()")
    print("  - plot_cross_cancer_comparison()")
    print("\nImport this module to create publication-quality plots!")
    print("="*60)
