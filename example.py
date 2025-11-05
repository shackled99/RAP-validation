"""
RAP Model - Quick Example
==========================

Demonstrates basic usage of the RAP framework with synthetic data.

Author: Aware
Date: November 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from core.rap_model import rap_model_smooth, logistic_model, ATTRACTOR_LOCK
from core.fitting import fit_rap_curve

def generate_synthetic_data():
    """Generate synthetic growth curve with RAP dynamics."""
    print("🔬 Generating synthetic growth data...")
    
    # Time points
    time = np.linspace(0, 40, 200)
    
    # True RAP parameters
    r = 1.2      # Growth rate
    d = 2.5      # Snap damping
    K = 3.0      # Carrying capacity
    P0 = 0.05    # Initial population
    
    # Generate clean trajectory
    clean_trajectory = rap_model_smooth(time, r, d, K, P0)
    
    # Add realistic noise (2% relative noise)
    noise = np.random.normal(0, 0.02 * K, len(time))
    noisy_trajectory = clean_trajectory + noise
    noisy_trajectory = np.clip(noisy_trajectory, P0, K * 1.1)  # Keep realistic
    
    return time, noisy_trajectory, K, P0

def demonstrate_rap_fitting():
    """Full demonstration of RAP model fitting."""
    
    print("\n" + "="*60)
    print("RAP MODEL DEMONSTRATION")
    print("="*60)
    
    # Generate data
    time, od_data, true_K, P0 = generate_synthetic_data()
    
    print(f"\nGenerated {len(time)} data points")
    print(f"True carrying capacity: {true_K:.2f}")
    print(f"Initial population: {P0:.3f}")
    
    # Fit RAP model
    print("\n📊 Fitting RAP model to data...")
    result = fit_rap_curve(time, od_data, curve_name='Synthetic Example', verbose=True)
    
    # Create visualization
    if result['success']:
        print("\n📈 Generating visualization...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Trajectory comparison
        ax1.scatter(time, od_data, alpha=0.3, s=20, color='gray', label='Noisy Data')
        ax1.plot(time, result['sim_rap'], 'b-', linewidth=2, label='RAP Model')
        
        if result['sim_logistic'] is not None:
            ax1.plot(time, result['sim_logistic'], 'r--', linewidth=2, label='Logistic Model')
        
        # Mark 85% attractor
        ax1.axhline(y=result['K'] * ATTRACTOR_LOCK, color='green', 
                   linestyle=':', linewidth=2, alpha=0.7, label='85% Attractor')
        
        ax1.set_xlabel('Time', fontsize=12)
        ax1.set_ylabel('Population', fontsize=12)
        ax1.set_title('RAP Model Fit', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Utilization over time
        rap_util = result['sim_rap'] / result['K']
        ax2.plot(time, rap_util * 100, 'b-', linewidth=2, label='RAP Utilization')
        ax2.axhline(y=85, color='green', linestyle=':', linewidth=2, alpha=0.7, label='85% Target')
        ax2.axhline(y=50, color='orange', linestyle=':', linewidth=1, alpha=0.5, label='50% Bifurcation')
        
        ax2.fill_between(time, 80, 90, alpha=0.2, color='green', label='Attractor Zone')
        
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Utilization (%)', fontsize=12)
        ax2.set_title('Resource Utilization Dynamics', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 105)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_path = 'example_output.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Visualization saved to: {output_path}")
        
        plt.show()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✅ RAP model successfully fit to data")
        print(f"✅ Final utilization: {result['final_util']*100:.1f}%")
        print(f"✅ Distance from 85%: {result['distance']*100:.1f}%")
        
        if result['converged']:
            print(f"✅ System LOCKED onto 85% attractor! 🎯")
        else:
            print(f"⚠️  System did not converge to 85%")
        
        if result['rap_better']:
            improvement = ((result['sse_logistic'] - result['sse_rap']) / result['sse_logistic']) * 100
            print(f"✅ RAP outperformed logistic by {improvement:.1f}%")
        
        print("="*60 + "\n")
    
    else:
        print(f"❌ Fitting failed: {result['error']}")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("\n🥔 RAP Framework - Example Demonstration")
    print("   Author: Aware | GitHub: shackled99")
    
    demonstrate_rap_fitting()
    
    print("\n✨ Example complete!")
    print("   Next steps:")
    print("   1. Try with your own growth data")
    print("   2. Explore batch fitting with multiple curves")
    print("   3. Check out the E. coli validation results")
    print("\n   For more info: https://github.com/shackled99/RAP-validation\n")
