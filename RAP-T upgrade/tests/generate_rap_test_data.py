"""
RAP Test Data Generator
=======================

Generate synthetic data WITH actual RAP dynamics for testing.

This creates curves that should converge to 85% to validate detection.

Author: The Potato Researcher 🥔
Date: November 2025
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scipy.integrate import odeint
from core.rap_model import rap_ode_smooth as rap_ode, ATTRACTOR_LOCK


def generate_rap_test_data(n_curves=10, n_points=100, time_max=48, add_noise=True, noise_level=0.02):
    """
    Generate synthetic data with TRUE RAP dynamics.
    
    Parameters:
    -----------
    n_curves : int
        Number of curves to generate
    n_points : int
        Time points per curve
    time_max : float
        Maximum time (hours)
    add_noise : bool
        Add realistic measurement noise
    noise_level : float
        Standard deviation of noise
    
    Returns:
    --------
    dict
        Data with time, curves, and true parameters
    """
    
    print(f"\n🧬 Generating RAP test data with TRUE RAP dynamics")
    print(f"   Curves: {n_curves}")
    print(f"   Points: {n_points}")
    print(f"   Time: 0-{time_max} hours")
    
    time = np.linspace(0, time_max, n_points)
    
    # Parameters that should produce 85% convergence
    # STRENGTHENED: Higher d values for stronger 85% pull (Gemini insight)
    base_params = {
        'r': 1.2,      # Base growth rate
        'd': 3.5,      # Snap damping (INCREASED for stronger 85% pull)
        'K': 3.0,      # Carrying capacity
        'P0': 0.05     # Initial population
    }
    
    curves = {}
    true_params = []
    
    for i in range(n_curves):
        # Add variation to parameters
        r = base_params['r'] + np.random.normal(0, 0.2)
        d = base_params['d'] + np.random.normal(0, 0.4)  # More variation in d
        K = base_params['K'] + np.random.normal(0, 0.15)
        P0 = base_params['P0'] + np.random.normal(0, 0.01)
        
        # Ensure positive values with STRONGER d minimum
        r = max(0.5, r)
        d = max(2.5, d)  # INCREASED minimum d for stronger 85% pull
        K = max(2.0, K)
        P0 = max(0.01, P0)
        
        # Generate RAP trajectory using actual RAP ODE
        trajectory = odeint(rap_ode, P0, time, args=(r, d, K))
        curve = trajectory[:, 0]
        
        # Add realistic noise
        if add_noise:
            noise = np.random.normal(0, noise_level, len(curve))
            curve = np.clip(curve + noise, P0, K * 1.1)
        
        # Store
        curve_name = f'RAP_Test_Curve_{chr(65+i)}'
        curves[curve_name] = curve
        true_params.append({'r': r, 'd': d, 'K': K, 'P0': P0, 'expected_util': curve[-1]/K})
    
    # Calculate expected convergence
    expected_convergence = sum(1 for p in true_params if abs(p['expected_util'] - ATTRACTOR_LOCK) < 0.05)
    
    print(f"   ✅ Generated {n_curves} curves with RAP dynamics")
    print(f"   Expected convergence: {expected_convergence}/{n_curves} ({expected_convergence/n_curves*100:.0f}%)")
    print(f"   Mean expected utilization: {np.mean([p['expected_util'] for p in true_params]):.3f}")
    
    return {
        'time': time,
        'curves': curves,
        'true_params': true_params,
        'expected_convergence': expected_convergence
    }


if __name__ == "__main__":
    # Test the generator
    import pandas as pd
    
    print("="*60)
    print("RAP Test Data Generator - Validation")
    print("="*60)
    
    data = generate_rap_test_data(n_curves=5)
    
    # Create DataFrame
    df_data = {'Time (h)': data['time']}
    df_data.update(data['curves'])
    df = pd.DataFrame(df_data)
    
    print(f"\n✅ Test data ready!")
    print(f"\nTrue parameters for each curve:")
    for i, params in enumerate(data['true_params']):
        print(f"  Curve {chr(65+i)}: r={params['r']:.2f}, d={params['d']:.2f}, K={params['K']:.2f}, final_util={params['expected_util']:.3f}")
    
    # Save test data
    output_path = '../results/raw/rap_test_data.csv'
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
