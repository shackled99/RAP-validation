"""Quick test of RAP model with d=3.5"""
import numpy as np
import sys
sys.path.insert(0, '..')
from core.rap_model import rap_model_smooth, ATTRACTOR_LOCK

# Test with d=3.5 (what we're using in data generator)
time = np.linspace(0, 40, 100)
trajectory = rap_model_smooth(
    time,
    growth_rate=1.2,
    snap_damping=3.5,  # HIGH d
    carrying_capacity=3.0,
    initial_population=0.05
)

final_util = trajectory[-1] / 3.0
print(f"Test with d=3.5:")
print(f"  Final utilization: {final_util:.3f}")
print(f"  Target: 0.850")
print(f"  Distance: {abs(final_util - 0.85):.3f}")
print(f"  Converged: {'YES' if abs(final_util - 0.85) < 0.05 else 'NO'}")

# Test trajectory at different points
print(f"\nTrajectory samples:")
for i in [25, 50, 75, 99]:
    util = trajectory[i] / 3.0
    print(f"  t={time[i]:.1f}: util={util:.3f}")
