"""
Cancer Growth RAP Fitting
==========================

Fit RAP model to cancer/tumor growth data and compare to Gompertz baseline.

The Gompertz model is the standard for tumor growth:
    dP/dt = r * P * ln(K/P)

We test if RAP provides superior fit with 85% attractor dynamics.

Author: Aware (with amnesiac OG Claude 🤖)
Date: November 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Import RAP framework
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.rap_model import rap_model_smooth, ATTRACTOR_LOCK, BIFURCATION_THRESHOLD
from core.fitting import fit_rap_curve
from datasets.biological.cancer.cancer_loader import (
    load_generic_growth_data,
    create_example_data,
    validate_data_format
)


def gompertz_model(time, r, K, P0):
    """
    Standard Gompertz model for tumor growth.
    
    Solution: P(t) = K * exp(-exp(-r*(t - t_inflection)))
    
    Simplified version:
    P(t) = K * (P0/K)^(exp(-r*t))
    
    Parameters:
    -----------
    time : array
        Time points
    r : float
        Growth rate
    K : float
        Carrying capacity
    P0 : float
        Initial population
    
    Returns:
    --------
    array
        Population at each time point
    """
    # Gompertz growth equation
    ratio = P0 / K
    return K * np.power(ratio, np.exp(-r * time))


def fit_gompertz_curve(time_data, volume_data, curve_name='Tumor', verbose=False):
    """
    Fit Gompertz model to tumor growth data.
    
    Parameters:
    -----------
    time_data : array
        Time points
    volume_data : array
        Tumor volume measurements
    curve_name : str
        Identifier
    verbose : bool
        Print results
    
    Returns:
    --------
    dict
        Fitting results
    """
    result = {
        'curve': curve_name,
        'success': False,
        'error': None
    }
    
    try:
        P0 = max(volume_data[0], 1e-6)
        K_est = max(volume_data) * 1.1
        
        # Fit Gompertz
        bounds = ([0.01, K_est * 0.5], [2.0, K_est * 2.0])
        p0 = [0.5, K_est]
        
        popt, _ = curve_fit(
            lambda t, r, K: gompertz_model(t, r, K, P0),
            time_data,
            volume_data,
            p0=p0,
            bounds=bounds,
            maxfev=5000
        )
        
        r_gomp, K_gomp = popt
        result['r'] = r_gomp
        result['K'] = K_gomp
        result['P0'] = P0
        
        # Simulate and calculate error
        sim_gomp = gompertz_model(time_data, r_gomp, K_gomp, P0)
        sse_gomp = np.sum((sim_gomp - volume_data) ** 2)
        
        result['sim_gompertz'] = sim_gomp
        result['sse_gompertz'] = sse_gomp
        result['final_util'] = sim_gomp[-1] / K_gomp
        result['success'] = True
        
        if verbose:
            print(f"\nGompertz fit: {curve_name}")
            print(f"  r = {r_gomp:.3f}, K = {K_gomp:.3f}")
            print(f"  SSE = {sse_gomp:.3f}")
            print(f"  Final util = {result['final_util']:.3f}")
        
    except Exception as e:
        result['error'] = str(e)
        if verbose:
            print(f"❌ Gompertz fit failed: {e}")
    
    return result


def compare_rap_vs_gompertz(time_data, volume_data, curve_name='Tumor', verbose=True):
    """
    Fit both RAP and Gompertz, compare results.
    
    Parameters:
    -----------
    time_data : array
        Time points
    volume_data : array
        Tumor volume measurements
    curve_name : str
        Identifier
    verbose : bool
        Print comparison
    
    Returns:
    --------
    dict
        Combined results with comparison metrics
    """
    # Fit RAP model
    rap_result = fit_rap_curve(time_data, volume_data, curve_name=curve_name, verbose=False)
    
    # Fit Gompertz model
    gomp_result = fit_gompertz_curve(time_data, volume_data, curve_name=curve_name, verbose=False)
    
    # Combine results
    comparison = {
        'curve': curve_name,
        'rap': rap_result,
        'gompertz': gomp_result,
    }
    
    # Calculate comparison metrics
    if rap_result['success'] and gomp_result['success']:
        rap_sse = rap_result['sse_rap']
        gomp_sse = gomp_result['sse_gompertz']
        
        comparison['rap_better'] = rap_sse < gomp_sse
        comparison['improvement_pct'] = ((gomp_sse - rap_sse) / gomp_sse) * 100
        comparison['sse_ratio'] = rap_sse / gomp_sse
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"MODEL COMPARISON: {curve_name}")
            print(f"{'='*60}")
            print(f"RAP Model:")
            print(f"  SSE: {rap_sse:.3f}")
            print(f"  Final utilization: {rap_result['final_util']:.3f} ({rap_result['final_util']*100:.1f}%)")
            print(f"  Converged to 85%: {'✅' if rap_result['converged'] else '❌'}")
            print(f"\nGompertz Model:")
            print(f"  SSE: {gomp_sse:.3f}")
            print(f"  Final utilization: {gomp_result['final_util']:.3f} ({gomp_result['final_util']*100:.1f}%)")
            print(f"\nComparison:")
            if comparison['rap_better']:
                print(f"  ✅ RAP superior by {comparison['improvement_pct']:.1f}%")
            else:
                print(f"  ❌ Gompertz superior by {-comparison['improvement_pct']:.1f}%")
            print(f"  SSE ratio (RAP/Gompertz): {comparison['sse_ratio']:.3f}")
            print(f"{'='*60}\n")
    
    return comparison


def batch_analyze_cancer_data(data_dict, verbose=False):
    """
    Analyze multiple tumor growth curves.
    
    Parameters:
    -----------
    data_dict : dict
        Data from cancer_loader functions
    verbose : bool
        Print individual results
    
    Returns:
    --------
    DataFrame
        Results for all curves
    """
    validate_data_format(data_dict)
    
    time = data_dict['time']
    curves = data_dict['data']
    
    results = []
    
    print(f"\n🔬 Analyzing {len(curves)} tumor growth curves...")
    print("="*60)
    
    for idx, (tumor_id, volume_data) in enumerate(curves.items(), 1):
        print(f"[{idx}/{len(curves)}] {tumor_id}...", end=' ')
        
        comparison = compare_rap_vs_gompertz(
            time, 
            volume_data, 
            curve_name=tumor_id,
            verbose=verbose
        )
        
        # Flatten for DataFrame
        row = {
            'tumor_id': tumor_id,
            'rap_success': comparison['rap']['success'],
            'rap_converged': comparison['rap'].get('converged', False),
            'rap_final_util': comparison['rap'].get('final_util', np.nan),
            'rap_sse': comparison['rap'].get('sse_rap', np.nan),
            'gomp_success': comparison['gompertz']['success'],
            'gomp_final_util': comparison['gompertz'].get('final_util', np.nan),
            'gomp_sse': comparison['gompertz'].get('sse_gompertz', np.nan),
            'rap_better': comparison.get('rap_better', False),
            'improvement_pct': comparison.get('improvement_pct', np.nan)
        }
        
        results.append(row)
        
        if row['rap_success']:
            status = "✅" if row['rap_converged'] else "⚠️"
            print(f"{status} util={row['rap_final_util']:.2f}")
        else:
            print("❌ Failed")
    
    df = pd.DataFrame(results)
    
    # Summary statistics
    print("\n" + "="*60)
    print("BATCH SUMMARY")
    print("="*60)
    
    successful = df[df['rap_success'] == True]
    
    if len(successful) > 0:
        conv_rate = successful['rap_converged'].sum() / len(successful)
        mean_util = successful['rap_final_util'].mean()
        std_util = successful['rap_final_util'].std()
        rap_better_rate = successful['rap_better'].sum() / len(successful)
        mean_improvement = successful['improvement_pct'].mean()
        
        print(f"Successful fits: {len(successful)}/{len(df)}")
        print(f"\nRAP Convergence:")
        print(f"  Converged to 85%: {successful['rap_converged'].sum()}/{len(successful)} ({conv_rate*100:.1f}%)")
        print(f"  Mean final util: {mean_util:.3f} ± {std_util:.3f}")
        print(f"  Distance from 85%: {abs(mean_util - ATTRACTOR_LOCK):.3f}")
        print(f"\nModel Comparison:")
        print(f"  RAP superior: {successful['rap_better'].sum()}/{len(successful)} ({rap_better_rate*100:.1f}%)")
        print(f"  Mean improvement: {mean_improvement:.1f}%")
        print("="*60 + "\n")
    
    return df


if __name__ == "__main__":
    print("\n🧬 Cancer Growth RAP Validation")
    print("   Testing universal 85% attractor in eukaryotic systems")
    print("="*60)
    
    # Generate synthetic cancer data
    print("\n📊 Generating synthetic tumor growth data...")
    cancer_data = create_example_data(n_curves=10, n_points=40, noise_level=0.03)
    
    print(f"✅ Generated {cancer_data['metadata']['n_samples']} tumors")
    print(f"   Time span: {cancer_data['time'][-1]:.0f} days")
    
    # Run batch analysis
    results_df = batch_analyze_cancer_data(cancer_data, verbose=False)
    
    # Save results
    output_path = Path(__file__).parent / 'results'
    output_path.mkdir(exist_ok=True)
    
    results_df.to_csv(output_path / 'synthetic_cancer_rap_results.csv', index=False)
    print(f"\n💾 Results saved to: {output_path / 'synthetic_cancer_rap_results.csv'}")
    
    print("\n✨ Cancer validation test complete!")
    print("   Ready for real tumor growth data!")
