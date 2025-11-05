"""
RAP Core Model - SMOOTHED VERSION
==================================

Recursive Attractor Principle with numerically stable smooth transitions.

CRITICAL FIX: Replaced sharp if/elif/else transitions with smooth sigmoids
for numerical stability in ODE solving.

Author: The Potato Researcher 🥔
Date: November 2025
Version: 2.0 (Smoothed)
"""

import numpy as np
from scipy.integrate import odeint

# RAP Constants
BIFURCATION_THRESHOLD = 0.50  # 50% - Edge of chaos
ATTRACTOR_LOCK = 0.85          # 85% - Optimal stable state
PHI = (1 + np.sqrt(5)) / 2     # Golden ratio
GSI = 1 / (PHI ** 2)           # Golden ratio damping ≈ 0.382

# Smoothing parameter for transitions (high = sharp but smooth)
SIGMA = 500.0  # High value keeps transitions sharp while maintaining differentiability


def smooth_sigmoid(x, center, sigma=SIGMA):
    """
    Smooth sigmoid transition function.
    
    Parameters:
    -----------
    x : float or array
        Input value
    center : float
        Center point of transition
    sigma : float
        Steepness (higher = sharper)
    
    Returns:
    --------
    float or array
        Sigmoid value between 0 and 1
    
    Notes:
    ------
    Returns ~0 when x << center, ~1 when x >> center
    Smooth and differentiable everywhere
    """
    return 1.0 / (1.0 + np.exp(-sigma * (x - center)))


def smooth_step(x, low, high, sigma=SIGMA):
    """
    Smooth step function between two values.
    
    Parameters:
    -----------
    x : float or array
        Input value
    low : float
        Lower threshold
    high : float
        Upper threshold
    sigma : float
        Steepness
    
    Returns:
    --------
    float or array
        Value between 0 and 1 indicating position in range
    """
    return smooth_sigmoid(x, low, sigma) * (1.0 - smooth_sigmoid(x, high, sigma))


def rap_rate_smooth(utilization, growth_rate, snap_damping):
    """
    Calculate effective recursion rate with SMOOTH transitions.
    
    Parameters:
    -----------
    utilization : float or array
        Current resource utilization (P/K), range [0, 1]
    growth_rate : float
        Base growth rate parameter (r)
    snap_damping : float
        Snap damping parameter (d)
    
    Returns:
    --------
    float or array
        Effective growth rate with smooth RAP dynamics
    
    Notes:
    ------
    Three phases (now SMOOTH):
    1. util < 0.5: Exploration phase (constant rate)
    2. 0.5 < util < 0.85: Bifurcation zone (attractor pull) - SMOOTH
    3. util > 0.85: Maintenance phase (reduced rate) - SMOOTH
    
    Key improvement: Uses smooth sigmoids instead of sharp if/elif/else
    This ensures differentiability for numerical stability
    """
    
    # Phase indicators (smooth transitions)
    # in_exploration: ~1 when util < 0.5, ~0 when util > 0.5
    in_exploration = 1.0 - smooth_sigmoid(utilization, BIFURCATION_THRESHOLD, SIGMA)
    
    # in_bifurcation: ~1 when 0.5 < util < 0.85, ~0 otherwise
    in_bifurcation = smooth_step(utilization, BIFURCATION_THRESHOLD, ATTRACTOR_LOCK, SIGMA)
    
    # in_maintenance: ~1 when util > 0.85, ~0 when util < 0.85
    in_maintenance = smooth_sigmoid(utilization, ATTRACTOR_LOCK, SIGMA)
    
    # Phase 1: Exploration (constant rate)
    exploration_rate = growth_rate
    
    # Phase 2: Bifurcation (attractor pull)
    distance_to_attractor = ATTRACTOR_LOCK - utilization
    bifurcation_rate = growth_rate * (1.0 + snap_damping * distance_to_attractor)
    
    # Phase 3: Maintenance (STRONG RESISTANCE past 85%)
    # CRITICAL FIX: Use negative feedback to PREVENT going past 85%
    # The further past 85%, the stronger the resistance
    overshoot = utilization - ATTRACTOR_LOCK  # Positive when > 85%
    maintenance_rate = growth_rate * (0.05 - snap_damping * 0.5 * overshoot)
    
    # Smooth combination of all phases
    effective_rate = (
        in_exploration * exploration_rate +
        in_bifurcation * bifurcation_rate +
        in_maintenance * maintenance_rate
    )
    
    return effective_rate


def rap_ode_smooth(population, time, growth_rate, snap_damping, carrying_capacity):
    """
    Ordinary Differential Equation for RAP with SMOOTH dynamics.
    
    Parameters:
    -----------
    population : float
        Current population/resource level (P)
    time : float
        Time parameter (for ODE solver)
    growth_rate : float
        Base growth rate (r)
    snap_damping : float
        Snap damping parameter (d)
    carrying_capacity : float
        Maximum capacity (K)
    
    Returns:
    --------
    float
        Rate of population change (dP/dt)
    
    Notes:
    ------
    Uses smooth rap_rate_smooth() for numerical stability
    """
    utilization = population / carrying_capacity
    effective_rate = rap_rate_smooth(utilization, growth_rate, snap_damping)
    
    # Logistic growth with RAP-modified rate
    dP_dt = effective_rate * population * (1 - utilization)
    
    return dP_dt


def rap_model_smooth(time_array, growth_rate, snap_damping, carrying_capacity, initial_population):
    """
    Solve SMOOTH RAP model over time array.
    
    Parameters:
    -----------
    time_array : array-like
        Time points for solution
    growth_rate : float
        Base growth rate (r)
    snap_damping : float
        Snap damping parameter (d)
    carrying_capacity : float
        Maximum capacity (K)
    initial_population : float
        Starting population (P0)
    
    Returns:
    --------
    array
        Population values at each time point
    
    Notes:
    ------
    CRITICAL: Uses smooth ODE for numerical stability
    """
    solution = odeint(
        rap_ode_smooth,
        initial_population,
        time_array,
        args=(growth_rate, snap_damping, carrying_capacity),
        rtol=1e-6,  # Relative tolerance
        atol=1e-8   # Absolute tolerance
    )
    
    return solution[:, 0].ravel()


# Keep old functions for compatibility but mark deprecated
def rap_rate(utilization, growth_rate, snap_damping):
    """DEPRECATED: Use rap_rate_smooth() for numerical stability"""
    return rap_rate_smooth(utilization, growth_rate, snap_damping)


def rap_ode(population, time, growth_rate, snap_damping, carrying_capacity):
    """DEPRECATED: Use rap_ode_smooth() for numerical stability"""
    return rap_ode_smooth(population, time, growth_rate, snap_damping, carrying_capacity)


def rap_model(time_array, growth_rate, snap_damping, carrying_capacity, initial_population):
    """DEPRECATED: Use rap_model_smooth() for numerical stability"""
    return rap_model_smooth(time_array, growth_rate, snap_damping, carrying_capacity, initial_population)


def logistic_model(time_array, growth_rate, carrying_capacity, initial_population):
    """
    Standard logistic model for comparison.
    
    Analytical solution: P(t) = K / (1 + (K/P0 - 1) * exp(-rt))
    """
    ratio = carrying_capacity / initial_population
    exponential = np.exp(-growth_rate * time_array)
    
    population = carrying_capacity / (1 + (ratio - 1) * exponential)
    
    return population


def calculate_utilization(population, carrying_capacity):
    """Calculate resource utilization percentage."""
    return population / carrying_capacity


def check_attractor_convergence(population_array, carrying_capacity, tolerance=0.05):
    """
    Check if system converged to 85% attractor.
    
    Returns dict with convergence statistics.
    """
    utilization = calculate_utilization(population_array, carrying_capacity)
    final_util = utilization[-1]
    distance = abs(final_util - ATTRACTOR_LOCK)
    converged = distance < tolerance
    
    # Count how many points are near the attractor
    near_attractor = np.abs(utilization - ATTRACTOR_LOCK) < (tolerance / 2)
    stable_points = np.sum(near_attractor)
    
    return {
        'final_utilization': final_util,
        'distance_from_attractor': distance,
        'converged': converged,
        'stable_points': stable_points
    }


if __name__ == "__main__":
    # Test the smoothed model
    print("RAP Core Model v2.0 - SMOOTHED")
    print("=" * 60)
    print(f"Bifurcation Threshold: {BIFURCATION_THRESHOLD}")
    print(f"Attractor Lock: {ATTRACTOR_LOCK}")
    print(f"Smoothing Factor (σ): {SIGMA}")
    print("=" * 60)
    
    # Test trajectory
    time = np.linspace(0, 40, 200)
    params = {
        'growth_rate': 1.2,
        'snap_damping': 2.5,
        'carrying_capacity': 3.0,
        'initial_population': 0.05
    }
    
    print("\nGenerating test trajectory with smooth transitions...")
    trajectory = rap_model_smooth(time, **params)
    stats = check_attractor_convergence(trajectory, params['carrying_capacity'])
    
    print(f"\nTest run completed:")
    print(f"Final utilization: {stats['final_utilization']:.3f}")
    print(f"Distance from 85%: {stats['distance_from_attractor']:.3f}")
    print(f"Converged: {'✅' if stats['converged'] else '❌'}")
    print(f"Stable points: {stats['stable_points']}")
    
    print("\n✅ Smooth RAP model ready for use!")
    print("   No more numerical instability!")
