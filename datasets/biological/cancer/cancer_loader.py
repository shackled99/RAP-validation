"""
Cancer Growth Data Loader
==========================

Utilities for loading and preprocessing cancer/tumor growth data.

Supports multiple data formats:
- Cell line growth curves (in vitro)
- Xenograft tumor volumes (in vivo)
- Clinical tumor measurements

Author: Aware (with OG Claude assist 🤖)
Date: November 2025
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent / 'data'


def load_generic_growth_data(filepath, time_col='time', value_col='volume', 
                             id_col=None, normalize=True):
    """
    Load generic growth curve data from CSV.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to CSV file
    time_col : str
        Name of time column
    value_col : str
        Name of measurement column (volume, cell count, etc.)
    id_col : str, optional
        Column identifying different samples/tumors
    normalize : bool
        Normalize to carrying capacity (max value per sample)
    
    Returns:
    --------
    dict
        {
            'time': array of time points,
            'data': dict of {sample_id: growth_values},
            'metadata': dict of additional info
        }
    """
    df = pd.read_csv(filepath)
    
    if id_col is None:
        # Single sample case
        time = df[time_col].values
        values = df[value_col].values
        
        if normalize:
            K = np.max(values)
            values = values / K
            metadata = {'K': K, 'normalized': True}
        else:
            metadata = {'normalized': False}
        
        return {
            'time': time,
            'data': {'sample_1': values},
            'metadata': metadata
        }
    
    else:
        # Multiple samples case
        samples = df[id_col].unique()
        time = None
        data = {}
        K_values = {}
        
        for sample in samples:
            sample_df = df[df[id_col] == sample].sort_values(time_col)
            
            if time is None:
                time = sample_df[time_col].values
            
            values = sample_df[value_col].values
            
            if normalize:
                K = np.max(values)
                values = values / K
                K_values[sample] = K
            
            data[sample] = values
        
        metadata = {
            'normalized': normalize,
            'n_samples': len(samples),
            'K_values': K_values if normalize else None
        }
        
        return {
            'time': time,
            'data': data,
            'metadata': metadata
        }


def load_xenograft_data(filepath, **kwargs):
    """
    Load xenograft tumor volume data.
    
    Expected format: CSV with columns [time, tumor_id, volume_mm3]
    
    Parameters:
    -----------
    filepath : str or Path
        Path to xenograft data CSV
    **kwargs : dict
        Additional arguments passed to load_generic_growth_data
    
    Returns:
    --------
    dict
        Formatted growth data
    """
    defaults = {
        'time_col': 'day',
        'value_col': 'volume_mm3',
        'id_col': 'tumor_id',
        'normalize': True
    }
    defaults.update(kwargs)
    
    return load_generic_growth_data(filepath, **defaults)


def load_cell_line_data(filepath, **kwargs):
    """
    Load cell line growth data (cell counts over time).
    
    Expected format: CSV with columns [time_hours, cell_line_id, cell_count]
    
    Parameters:
    -----------
    filepath : str or Path
        Path to cell line data CSV
    **kwargs : dict
        Additional arguments passed to load_generic_growth_data
    
    Returns:
    --------
    dict
        Formatted growth data
    """
    defaults = {
        'time_col': 'time_hours',
        'value_col': 'cell_count',
        'id_col': 'cell_line',
        'normalize': True
    }
    defaults.update(kwargs)
    
    return load_generic_growth_data(filepath, **defaults)


def create_example_data(n_curves=10, n_points=50, noise_level=0.05):
    """
    Generate synthetic cancer growth data for testing.
    
    Simulates tumor growth with RAP dynamics + noise.
    
    Parameters:
    -----------
    n_curves : int
        Number of tumor growth curves to generate
    n_points : int
        Number of time points per curve
    noise_level : float
        Relative noise level (e.g., 0.05 = 5% noise)
    
    Returns:
    --------
    dict
        Synthetic growth data in standard format
    """
    from core.rap_model import rap_model_smooth
    
    time = np.linspace(0, 30, n_points)  # 30 days
    data = {}
    
    for i in range(n_curves):
        # Vary parameters slightly for each tumor
        r = np.random.uniform(0.8, 1.5)      # Growth rate
        d = np.random.uniform(1.5, 3.5)      # Snap damping
        K = np.random.uniform(800, 1200)     # Carrying capacity (mm³)
        P0 = np.random.uniform(10, 50)       # Initial volume
        
        # Generate clean trajectory
        clean_trajectory = rap_model_smooth(time, r, d, K, P0)
        
        # Add realistic noise
        noise = np.random.normal(0, noise_level * K, n_points)
        noisy_trajectory = clean_trajectory + noise
        noisy_trajectory = np.clip(noisy_trajectory, P0, K * 1.1)
        
        # Normalize to K
        data[f'tumor_{i+1}'] = noisy_trajectory / K
    
    return {
        'time': time,
        'data': data,
        'metadata': {
            'n_samples': n_curves,
            'normalized': True,
            'synthetic': True
        }
    }


def validate_data_format(data_dict):
    """
    Validate that loaded data is in correct format.
    
    Parameters:
    -----------
    data_dict : dict
        Data dictionary to validate
    
    Returns:
    --------
    bool
        True if valid, raises ValueError if not
    """
    required_keys = ['time', 'data', 'metadata']
    
    for key in required_keys:
        if key not in data_dict:
            raise ValueError(f"Missing required key: {key}")
    
    if not isinstance(data_dict['time'], np.ndarray):
        raise ValueError("'time' must be numpy array")
    
    if not isinstance(data_dict['data'], dict):
        raise ValueError("'data' must be dict of growth curves")
    
    if len(data_dict['data']) == 0:
        raise ValueError("No growth curves in data")
    
    # Check all curves have same length as time
    n_time = len(data_dict['time'])
    for sample_id, values in data_dict['data'].items():
        if len(values) != n_time:
            raise ValueError(f"Sample {sample_id} length mismatch: {len(values)} vs {n_time}")
    
    return True


def get_available_datasets():
    """
    List available datasets in the data directory.
    
    Returns:
    --------
    list
        List of available dataset filenames
    """
    if not DATA_DIR.exists():
        return []
    
    datasets = list(DATA_DIR.glob('*.csv'))
    return [d.name for d in datasets]


if __name__ == "__main__":
    print("Cancer Data Loader - Test Mode")
    print("=" * 60)
    
    # Generate and test synthetic data
    print("\n📊 Generating synthetic cancer growth data...")
    synthetic = create_example_data(n_curves=5, n_points=30)
    
    print(f"✅ Generated {synthetic['metadata']['n_samples']} tumor growth curves")
    print(f"   Time points: {len(synthetic['time'])}")
    print(f"   Time range: {synthetic['time'][0]:.1f} to {synthetic['time'][-1]:.1f} days")
    
    # Validate format
    print("\n🔍 Validating data format...")
    try:
        validate_data_format(synthetic)
        print("✅ Data format valid!")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")
    
    # Check available datasets
    print(f"\n📁 Available datasets in {DATA_DIR}:")
    datasets = get_available_datasets()
    if datasets:
        for ds in datasets:
            print(f"   - {ds}")
    else:
        print("   (No datasets found - add CSV files to data/ folder)")
    
    print("\n" + "=" * 60)
    print("✨ Cancer data loader ready!")
    print("   Use create_example_data() to generate test data")
    print("   Or load_generic_growth_data() for real datasets")
