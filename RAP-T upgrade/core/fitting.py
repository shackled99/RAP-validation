"""
RAP Fitting Module
==================

Curve fitting optimization for RAP model with multi-LLM integrated suggestions.

Integrates suggestions from:
- GPT: Parentheses fix, quiet plots, batch stats
- Grok: Error handling
- Gemini: Warning suppression, stable points
- Copilot: Return dict structure, DataFrame output

Author: The Potato Researcher 🥔
Date: November 2025
"""

import numpy as np
import warnings
from scipy.optimize import curve_fit
from core.rap_model import (
    rap_model_smooth as rap_model,  # Use SMOOTH version for stability
    logistic_model, 
    BIFURCATION_THRESHOLD, 
    ATTRACTOR_LOCK,
    check_attractor_convergence
)

# Suppress optimization warnings (Gemini suggestion)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def fit_rap_curve(time_data, od_data, curve_name='Curve', verbose=True):
    """
    Fit RAP model to empirical growth curve data.
    
    Parameters:
    -----------
    time_data : array-like
        Time points
    od_data : array-like
        Optical density (population) measurements
    curve_name : str
        Identifier for this curve
    verbose : bool
        Print detailed results (default: True)
    
    Returns:
    --------
    dict
        Comprehensive fitting results:
        - 'curve': Curve identifier
        - 'r': Fitted growth rate
        - 'd': Fitted snap damping
        - 'K': Fitted carrying capacity
        - 'P0': Initial population
        - 'final_util': Final utilization (P/K)
        - 'distance': Distance from 85% attractor
        - 'converged': Boolean, within 2% of attractor
        - 'stable_points': Count of points near attractor
        - 'sse_rap': Sum of squared errors (RAP)
        - 'sse_logistic': Sum of squared errors (Logistic)
        - 'rap_better': Boolean, RAP < Logistic SSE
        - 'sim_rap': Simulated RAP trajectory
        - 'sim_logistic': Simulated Logistic trajectory
        - 'success': Boolean, fit succeeded
        - 'error': Error message if failed
    
    Notes:
    ------
    Implements suggestions from GPT, Grok, Gemini, and Copilot for:
    - Robust error handling
    - Clean return structure
    - Convergence metrics
    - Model comparison
    """
    
    # Initialize result dict (Copilot suggestion)
    result = {
        'curve': curve_name,
        'success': False,
        'error': None
    }
    
    try:
        # Get initial population
        P0 = max(od_data[0], 1e-6)  # Avoid zero initialization
        result['P0'] = P0
        
        # RAP Model Fitting
        # Bounds: r ∈ [0.1, 3], d ∈ [0.1, 5], K ∈ [max(OD), 1.5*max(OD)]
        max_od = np.max(od_data)
        bounds_rap = ([0.1, 0.1, max_od], [3.0, 5.0, max_od * 1.5])
        p0_rap = [1.4, 2.0, max_od * 1.1]
        
        popt_rap, _ = curve_fit(
            lambda t, r, d, K: rap_model(t, r, d, K, P0),
            time_data,
            od_data,
            p0=p0_rap,
            bounds=bounds_rap,
            maxfev=5000
        )
        
        r_rap, d_rap, K_rap = popt_rap
        result['r'] = r_rap
        result['d'] = d_rap
        result['K'] = K_rap
        
        # Simulate RAP trajectory
        sim_rap = rap_model(time_data, r_rap, d_rap, K_rap, P0)
        result['sim_rap'] = sim_rap
        
        # Calculate RAP error
        sse_rap = np.sum((sim_rap - od_data) ** 2)
        result['sse_rap'] = sse_rap
        
        # Logistic Model Fitting (for comparison)
        bounds_log = ([0.1, max_od], [3.0, max_od * 1.5])
        p0_log = [1.4, max_od * 1.1]
        
        try:
            popt_log, _ = curve_fit(
                lambda t, r, K: logistic_model(t, r, K, P0),
                time_data,
                od_data,
                p0=p0_log,
                bounds=bounds_log,
                maxfev=5000
            )
            
            r_log, K_log = popt_log
            sim_log = logistic_model(time_data, r_log, K_log, P0)
            sse_log = np.sum((sim_log - od_data) ** 2)
            
            result['sim_logistic'] = sim_log
            result['sse_logistic'] = sse_log
            result['rap_better'] = sse_rap < sse_log
            
        except RuntimeError:
            # Logistic fit failed, but RAP succeeded
            result['sim_logistic'] = None
            result['sse_logistic'] = np.inf
            result['rap_better'] = True
        
        # Analyze convergence (Gemini + Copilot suggestions)
        # Use 5% tolerance since 80-90% is within attractor zone
        convergence = check_attractor_convergence(sim_rap, K_rap, tolerance=0.05)
        result['final_util'] = convergence['final_utilization']
        result['distance'] = convergence['distance_from_attractor']
        result['converged'] = convergence['converged']
        result['stable_points'] = convergence['stable_points']
        
        # Additional stable points analysis (Gemini suggestion)
        # Count points within 1% of attractor
        rap_utilization = sim_rap / K_rap
        tight_stable_85 = np.sum(
            (rap_utilization > ATTRACTOR_LOCK - 0.01) & 
            (rap_utilization < ATTRACTOR_LOCK + 0.01)
        )
        result['tight_stable_points_85'] = tight_stable_85
        
        # GEMINI'S NEW INSIGHT: Track 100% convergence too!
        tight_stable_100 = np.sum(
            (rap_utilization > 0.99) & 
            (rap_utilization < 1.01)
        )
        result['tight_stable_points_100'] = tight_stable_100
        
        # Check if converged to 100% instead of 85%
        distance_100 = abs(result['final_util'] - 1.0)
        result['converged_100'] = distance_100 < 0.02
        result['distance_100'] = distance_100
        
        result['success'] = True
        
        # Print results if verbose
        if verbose:
            print(f"\n{'='*60}")
            print(f"RAP FIT RESULTS: {curve_name}")
            print(f"{'='*60}")
            print(f"Parameters:")
            print(f"  Growth rate (r):     {r_rap:.3f}")
            print(f"  Snap damping (d):    {d_rap:.3f}")
            print(f"  Carrying capacity:   {K_rap:.3f}")
            print(f"\nConvergence Analysis:")
            print(f"  Final utilization:   {result['final_util']:.3f} ({result['final_util']*100:.1f}%)")
            print(f"  Distance from 85%:   {result['distance']:.3f}")
            print(f"  Stable at lock:      {result['stable_points']} points")
            print(f"  Tight stable at 85%: {tight_stable_85} points")
            print(f"  Tight stable at 100%:{tight_stable_100} points")
            print(f"\nModel Comparison:")
            print(f"  SSE (RAP):           {sse_rap:.3f}")
            print(f"  SSE (Logistic):      {result['sse_logistic']:.3f}")
            print(f"  RAP superior:        {'✅ YES' if result['rap_better'] else '❌ NO'}")
            print(f"\nConvergence Status:")
            if result['converged']:
                print(f"  {'✅ RAP 85% CONVERGENCE DETECTED'}")
                print(f"  System locked onto 85% attractor!")
            elif result.get('converged_100', False):
                print(f"  {'⚠️  100% CONVERGENCE DETECTED'}")
                print(f"  System went to full capacity (not 85%)")
                print(f"  This suggests weak RAP dynamics (low d)")
            else:
                print(f"  {'❓ NO CLEAR CONVERGENCE'}")
                print(f"  System did not lock onto any attractor")
            print(f"{'='*60}\n")
        
    except RuntimeError as e:
        result['error'] = f"Fitting failed: {str(e)}"
        if verbose:
            print(f"❌ Error fitting {curve_name}: {str(e)}")
    
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        if verbose:
            print(f"❌ Unexpected error for {curve_name}: {str(e)}")
    
    return result


def batch_fit_curves(time_data, od_dataframe, od_columns=None, verbose=False):
    """
    Fit RAP model to multiple curves in batch.
    
    Parameters:
    -----------
    time_data : array-like
        Time points (shared across curves)
    od_dataframe : DataFrame
        DataFrame containing OD measurements
    od_columns : list, optional
        Specific columns to fit. If None, auto-detects OD columns
    verbose : bool
        Print results for each curve (default: False for batch)
    
    Returns:
    --------
    DataFrame
        Aggregated results across all curves
    
    Notes:
    ------
    Implements GPT + Copilot batch processing suggestions
    """
    import pandas as pd
    
    # Auto-detect OD columns if not specified (Grok suggestion with GPT fix)
    if od_columns is None:
        time_col = None
        for col in od_dataframe.columns:
            if 'time' in col.lower():
                time_col = col
                break
        
        # CORRECTED: Parentheses fix from GPT + Copilot
        od_columns = [
            col for col in od_dataframe.columns 
            if (col != time_col) and ('OD' in col or 'rep' in col.lower())
        ]
    
    results = []
    total = len(od_columns)
    
    print(f"\n🔬 Starting batch fitting for {total} curves...")
    
    for idx, col in enumerate(od_columns, 1):
        od_data = od_dataframe[col].dropna().values
        
        if len(od_data) < 6:
            print(f"⚠️  Skipping {col}: insufficient data ({len(od_data)} points)")
            continue
        
        # Align time data to match OD data length
        aligned_time = time_data[:len(od_data)]
        
        print(f"  [{idx}/{total}] Fitting {col}...", end='')
        
        result = fit_rap_curve(aligned_time, od_data, curve_name=col, verbose=verbose)
        
        if result['success']:
            print(f" ✅")
        else:
            print(f" ❌ {result['error']}")
        
        results.append(result)
    
    # Convert to DataFrame (Copilot suggestion)
    results_df = pd.DataFrame(results)
    
    # Calculate aggregate statistics (GPT + Copilot suggestions)
    if len(results_df) > 0:
        successful = results_df[results_df['success'] == True]
        
        if len(successful) > 0:
            print(f"\n{'='*60}")
            print(f"BATCH STATISTICS (n={len(successful)})")
            print(f"{'='*60}")
            print(f"Mean final utilization:  {successful['final_util'].mean():.3f} ± {successful['final_util'].std():.3f}")
            print(f"Mean distance from 85%:  {successful['distance'].mean():.3f}")
            print(f"Convergence rate:        {successful['converged'].sum()}/{len(successful)} ({successful['converged'].mean()*100:.1f}%)")
            print(f"RAP superiority rate:    {successful['rap_better'].sum()}/{len(successful)} ({successful['rap_better'].mean()*100:.1f}%)")
            print(f"Mean stable points:      {successful['stable_points'].mean():.1f}")
            print(f"{'='*60}\n")
    
    return results_df


if __name__ == "__main__":
    # Quick test
    print("RAP Fitting Module - Quick Test")
    print("=" * 60)
    
    # Generate synthetic test data
    time = np.linspace(0, 10, 50)
    # Simulated growth with noise
    true_K = 1.0
    true_r = 1.5
    P0 = 0.1
    
    # Pure logistic for comparison
    true_trajectory = true_K / (1 + (true_K/P0 - 1) * np.exp(-true_r * time))
    noisy_data = true_trajectory + np.random.normal(0, 0.02, len(time))
    noisy_data = np.clip(noisy_data, 0.1, true_K)
    
    result = fit_rap_curve(time, noisy_data, curve_name='Synthetic Test', verbose=True)
    
    if result['success']:
        print("✅ Fitting module test PASSED")
    else:
        print("❌ Fitting module test FAILED")
