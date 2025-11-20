"""
RAP Visualization Module
========================

Enhanced plotting with phase reference lines and batch control.

Integrates suggestions from:
- Gemini: Phase reference lines, enhanced aesthetics
- GPT: Quiet plot toggle
- Copilot: Batch-friendly plotting

Author: The Potato Researcher 🥔
Date: November 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from core.rap_model import BIFURCATION_THRESHOLD, ATTRACTOR_LOCK


def plot_rap_fit(time_data, od_data, result, show_plot=True, save_path=None):
    """
    Create enhanced visualization of RAP fit with phase reference lines.
    
    Parameters:
    -----------
    time_data : array-like
        Time points
    od_data : array-like
        Observed OD data
    result : dict
        Fitting result from fit_rap_curve()
    show_plot : bool
        Display plot interactively (default: True)
        Set False for batch processing (GPT/Copilot suggestion)
    save_path : str, optional
        Path to save figure. If None, doesn't save
    
    Notes:
    ------
    Implements Gemini's enhanced visualization with:
    - Phase reference lines (50% bifurcation, 85% attractor)
    - Professional color scheme
    - Clear legends and labels
    - Carrying capacity indicator
    """
    
    if not result['success']:
        print(f"⚠️  Cannot plot {result['curve']}: Fit failed")
        return
    
    # Create figure with appropriate size
    plt.figure(figsize=(10, 6))
    
    # Plot data and fits
    plt.plot(
        time_data, 
        od_data, 
        'o', 
        color='#1f77b4', 
        markersize=4, 
        label='Experimental Data',
        alpha=0.6
    )
    
    plt.plot(
        time_data, 
        result['sim_rap'], 
        '-', 
        color='#d62728', 
        linewidth=2.5, 
        label=f'RAP Fit (SSE: {result["sse_rap"]:.3f})'
    )
    
    if result['sim_logistic'] is not None:
        plt.plot(
            time_data, 
            result['sim_logistic'], 
            '--', 
            color='#2ca02c', 
            linewidth=2, 
            label=f'Logistic Fit (SSE: {result["sse_logistic"]:.3f})'
        )
    
    # Add RAP phase reference lines (Gemini suggestion)
    K = result['K']
    
    # 50% Bifurcation threshold
    plt.axhline(
        y=K * BIFURCATION_THRESHOLD, 
        color='#ff7f0e', 
        linestyle='-.', 
        alpha=0.6, 
        linewidth=1.5,
        label=f'{int(BIFURCATION_THRESHOLD*100)}% Bifurcation Threshold'
    )
    
    # 85% Attractor lock
    plt.axhline(
        y=K * ATTRACTOR_LOCK, 
        color='#9467bd', 
        linestyle=':', 
        alpha=0.9, 
        linewidth=2.5,
        label=f'{int(ATTRACTOR_LOCK*100)}% Attractor Lock'
    )
    
    # Carrying capacity
    plt.axhline(
        y=K, 
        color='gray', 
        linestyle='--', 
        alpha=0.5, 
        linewidth=1,
        label=f'K (Carrying Capacity)'
    )
    
    # Labels and title
    plt.xlabel('Time (hours)', fontsize=12)
    plt.ylabel('OD600 (Population)', fontsize=12)
    
    # Title with convergence status
    convergence_status = '✅ CONVERGED' if result['converged'] else '❓ NOT CONVERGED'
    plt.title(
        f'RAP Model Fit: {result["curve"]}\n{convergence_status} to 85% Attractor',
        fontsize=13,
        fontweight='bold'
    )
    
    # Legend
    plt.legend(loc='lower right', fontsize=9)
    
    # Grid
    plt.grid(True, linestyle=':', alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  📊 Plot saved: {save_path}")
    
    # Show or close (GPT/Copilot suggestion for batch processing)
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_utilization_trajectory(time_data, result, show_plot=True, save_path=None):
    """
    Plot resource utilization over time with phase regions.
    
    Parameters:
    -----------
    time_data : array-like
        Time points
    result : dict
        Fitting result from fit_rap_curve()
    show_plot : bool
        Display plot interactively
    save_path : str, optional
        Path to save figure
    """
    
    if not result['success']:
        print(f"⚠️  Cannot plot utilization for {result['curve']}: Fit failed")
        return
    
    # Calculate utilization
    utilization = result['sim_rap'] / result['K']
    
    plt.figure(figsize=(10, 6))
    
    # Plot utilization
    plt.plot(time_data, utilization, '-', color='#1f77b4', linewidth=2.5, label='Resource Utilization')
    
    # Phase regions (Gemini enhancement)
    plt.axhspan(0, BIFURCATION_THRESHOLD, alpha=0.1, color='green', label='Exploration Phase')
    plt.axhspan(BIFURCATION_THRESHOLD, ATTRACTOR_LOCK, alpha=0.1, color='orange', label='Bifurcation Zone')
    plt.axhspan(ATTRACTOR_LOCK, 1.0, alpha=0.1, color='red', label='Maintenance Phase')
    
    # Reference lines
    plt.axhline(y=BIFURCATION_THRESHOLD, color='orange', linestyle='-.', alpha=0.6, linewidth=1.5)
    plt.axhline(y=ATTRACTOR_LOCK, color='purple', linestyle=':', alpha=0.9, linewidth=2.5)
    
    # Labels
    plt.xlabel('Time (hours)', fontsize=12)
    plt.ylabel('Resource Utilization (P/K)', fontsize=12)
    plt.title(f'RAP Utilization Trajectory: {result["curve"]}', fontsize=13, fontweight='bold')
    
    # Set y-axis limits
    plt.ylim(0, 1.05)
    
    plt.legend(loc='right', fontsize=9)
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_batch_summary(results_df, show_plot=True, save_path=None):
    """
    Create summary visualization for batch results.
    
    Parameters:
    -----------
    results_df : DataFrame
        Results from batch_fit_curves()
    show_plot : bool
        Display plot interactively
    save_path : str, optional
        Path to save figure
    """
    
    successful = results_df[results_df['success'] == True]
    
    if len(successful) == 0:
        print("⚠️  No successful fits to visualize")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Final Utilization Distribution
    ax1 = axes[0, 0]
    ax1.hist(successful['final_util'], bins=30, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax1.axvline(x=ATTRACTOR_LOCK, color='red', linestyle='--', linewidth=2, label='85% Attractor')
    ax1.axvline(x=successful['final_util'].mean(), color='green', linestyle=':', linewidth=2, label='Mean')
    ax1.set_xlabel('Final Utilization')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Final Utilization')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Distance from Attractor
    ax2 = axes[0, 1]
    ax2.hist(successful['distance'], bins=30, color='#ff7f0e', alpha=0.7, edgecolor='black')
    ax2.axvline(x=0.02, color='red', linestyle='--', linewidth=2, label='2% Threshold')
    ax2.set_xlabel('Distance from 85%')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Convergence Distance Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. SSE Comparison
    ax3 = axes[1, 0]
    converged = successful[successful['converged'] == True]
    not_converged = successful[successful['converged'] == False]
    
    if len(converged) > 0:
        ax3.scatter(converged['sse_rap'], converged['sse_logistic'], 
                   alpha=0.6, s=50, color='green', label='Converged')
    if len(not_converged) > 0:
        ax3.scatter(not_converged['sse_rap'], not_converged['sse_logistic'], 
                   alpha=0.6, s=50, color='red', label='Not Converged')
    
    # Diagonal line (equal SSE)
    max_sse = max(successful['sse_rap'].max(), successful['sse_logistic'].max())
    ax3.plot([0, max_sse], [0, max_sse], 'k--', alpha=0.5, label='Equal SSE')
    
    ax3.set_xlabel('RAP SSE')
    ax3.set_ylabel('Logistic SSE')
    ax3.set_title('Model Comparison: RAP vs Logistic')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Convergence Summary
    ax4 = axes[1, 1]
    convergence_counts = [
        successful['converged'].sum(),
        len(successful) - successful['converged'].sum()
    ]
    colors = ['#2ca02c', '#d62728']
    ax4.pie(convergence_counts, labels=['Converged', 'Not Converged'], 
            autopct='%1.1f%%', colors=colors, startangle=90)
    ax4.set_title(f'Convergence Rate\n(n={len(successful)})')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  📊 Batch summary saved: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    print("RAP Visualization Module - Quick Test")
    print("=" * 60)
    print("Module loaded successfully!")
    print("Use plot_rap_fit() to visualize individual fits")
    print("Use plot_batch_summary() for batch results")
    print("Set show_plot=False for batch processing")
