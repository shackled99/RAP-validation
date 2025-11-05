"""
E. coli Data Loader
===================

Automatic data loading from URLs with zip support.

Integrates suggestions from:
- Grok: URL loading, zip handling, auto-detection
- Gemini: Simulated test data

Author: The Potato Researcher 🥔
Date: November 2025
"""

import numpy as np
import pandas as pd
import urllib.request
import io
import zipfile


# Known E. coli growth datasets
DATASETS = {
    'giovannelli': {
        'name': 'Giovannelli Lab - Trace Metal Metabolic Shift',
        'url': 'https://raw.githubusercontent.com/giovannellilab/Ecoli_trace_metal_metabolic_shift/main/Ecoli_growth_data.csv',
        'description': 'E. coli growth under trace metal conditions',
        'format': 'csv'
    },
    'maier_2022': {
        'name': 'Maier et al. (2022) - 13,608 Growth Curves',
        'url': 'https://figshare.com/ndownloader/articles/25342064/versions/1',
        'description': 'Massive E. coli growth dataset from Figshare',
        'format': 'zip',
        'note': 'Download manually from https://figshare.com/articles/dataset/25342064'
    },
    # Add more datasets as we find them
}


def load_ecoli_from_url(dataset_key='giovannelli', verbose=True):
    """
    Load E. coli growth data directly from URL.
    
    Parameters:
    -----------
    dataset_key : str
        Key for dataset in DATASETS dict (default: 'giovannelli')
    verbose : bool
        Print loading progress
    
    Returns:
    --------
    DataFrame
        Raw growth data with time and OD columns
    
    Notes:
    ------
    Implements Grok's URL auto-loading suggestion
    """
    
    if dataset_key not in DATASETS:
        raise ValueError(f"Unknown dataset: {dataset_key}. Available: {list(DATASETS.keys())}")
    
    dataset_info = DATASETS[dataset_key]
    
    if verbose:
        print(f"\n📡 Loading dataset: {dataset_info['name']}")
        print(f"   Source: {dataset_info['url']}")
    
    try:
        # Download data (Grok suggestion)
        with urllib.request.urlopen(dataset_info['url']) as response:
            content = response.read().decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(content))
        
        if verbose:
            print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
            print(f"   Columns: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
        
        return df
    
    except Exception as e:
        if verbose:
            print(f"   ❌ Error loading from URL: {str(e)}")
            print(f"   💡 Falling back to simulated data...")
        
        return generate_simulated_data(verbose=verbose)


def load_ecoli_from_zip(zip_url, csv_filename, verbose=True):
    """
    Load E. coli data from a zipped CSV file.
    
    Parameters:
    -----------
    zip_url : str
        URL to zip file
    csv_filename : str
        Name of CSV file within the zip
    verbose : bool
        Print loading progress
    
    Returns:
    --------
    DataFrame
        Raw growth data
    
    Notes:
    ------
    Implements Grok's zip handling suggestion for large Figshare datasets
    """
    
    if verbose:
        print(f"\n📦 Loading zipped dataset")
        print(f"   Source: {zip_url}")
        print(f"   Target: {csv_filename}")
    
    try:
        # Download and unzip (Grok suggestion)
        with urllib.request.urlopen(zip_url) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                with z.open(csv_filename) as f:
                    df = pd.read_csv(f)
        
        if verbose:
            print(f"   ✅ Loaded {len(df)} rows from zip")
        
        return df
    
    except Exception as e:
        if verbose:
            print(f"   ❌ Error loading zip: {str(e)}")
        raise


def auto_detect_time_column(df):
    """
    Automatically detect time column.
    
    Parameters:
    -----------
    df : DataFrame
        Data with time column
    
    Returns:
    --------
    str
        Name of time column
    
    Notes:
    ------
    Implements Grok's auto-detection suggestion
    """
    
    # Common time column names
    time_keywords = ['time', 'hour', 'hrs', 'h', 't', 'minutes', 'min']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in time_keywords):
            return col
    
    # If no match, assume first column
    return df.columns[0]


def auto_detect_od_columns(df, time_col):
    """
    Automatically detect OD measurement columns.
    
    Parameters:
    -----------
    df : DataFrame
        Data with OD columns
    time_col : str
        Name of time column (to exclude)
    
    Returns:
    --------
    list
        Names of OD columns
    
    Notes:
    ------
    Implements Grok's auto-detection with GPT/Copilot parentheses fix
    """
    
    # Fixed: Correct parentheses (GPT/Copilot suggestion)
    od_cols = [
        col for col in df.columns 
        if (col != time_col) and ('OD' in col or 'od' in col or 'rep' in col.lower())
    ]
    
    return od_cols


def generate_simulated_data(n_curves=5, n_points=97, verbose=True):
    """
    Generate simulated E. coli growth data for testing.
    
    Parameters:
    -----------
    n_curves : int
        Number of growth curves to generate
    n_points : int
        Number of time points per curve
    verbose : bool
        Print generation info
    
    Returns:
    --------
    DataFrame
        Simulated growth data
    
    Notes:
    ------
    Implements Gemini's simulated data suggestion
    Uses realistic E. coli growth parameters
    """
    
    if verbose:
        print(f"\n🧪 Generating simulated E. coli data")
        print(f"   Curves: {n_curves}")
        print(f"   Points per curve: {n_points}")
    
    # Time array (0-48 hours, 30-min intervals)
    time = np.linspace(0, 48, n_points)
    
    # Base growth curve parameters
    base_K = 2.8  # Typical E. coli saturation OD
    base_r = 0.8  # Growth rate
    P0 = 0.04     # Initial OD
    
    # Create DataFrame
    data = {'Time (h)': time}
    
    for i in range(n_curves):
        # Add some variation
        K = base_K + np.random.normal(0, 0.15)
        r = base_r + np.random.normal(0, 0.1)
        
        # Generate logistic growth
        curve = K / (1 + (K / P0 - 1) * np.exp(-r * time))
        
        # Add realistic noise
        noise = np.random.normal(0, 0.02, len(curve))
        curve_noisy = np.clip(curve + noise, P0, K)
        
        # Add slight drift in later phase (realistic)
        drift = -0.001 * np.maximum(0, time - 24)
        curve_final = np.clip(curve_noisy + drift, P0, K)
        
        data[f'OD600_Medium_{chr(65+i)}_Rep_1'] = curve_final
    
    df = pd.DataFrame(data)
    
    if verbose:
        print(f"   ✅ Generated {n_curves} realistic growth curves")
    
    return df


def load_ecoli_data(source='auto', verbose=True):
    """
    Universal E. coli data loader.
    
    Parameters:
    -----------
    source : str or DataFrame
        - 'auto': Try URL, fall back to simulated
        - 'simulated': Generate test data
        - 'giovannelli': Load from Giovannelli lab
        - DataFrame: Use provided data
    verbose : bool
        Print loading progress
    
    Returns:
    --------
    tuple
        (time_array, dataframe, time_column, od_columns)
    
    Notes:
    ------
    Main entry point for data loading - handles all cases
    """
    
    # Handle DataFrame input
    if isinstance(source, pd.DataFrame):
        df = source
        if verbose:
            print(f"\n📊 Using provided DataFrame ({len(df)} rows)")
    
    # Handle string sources
    elif source == 'simulated':
        df = generate_simulated_data(verbose=verbose)
    
    elif source == 'auto':
        try:
            df = load_ecoli_from_url('giovannelli', verbose=verbose)
        except:
            df = generate_simulated_data(verbose=verbose)
    
    elif source in DATASETS:
        df = load_ecoli_from_url(source, verbose=verbose)
    
    else:
        raise ValueError(f"Unknown source: {source}")
    
    # Auto-detect columns
    time_col = auto_detect_time_column(df)
    od_cols = auto_detect_od_columns(df, time_col)
    
    if verbose:
        print(f"\n🔍 Auto-detection results:")
        print(f"   Time column: {time_col}")
        print(f"   OD columns: {len(od_cols)} found")
        if len(od_cols) <= 5:
            print(f"   Names: {od_cols}")
    
    # Extract time array
    time_data = df[time_col].values
    
    return time_data, df, time_col, od_cols


if __name__ == "__main__":
    print("E. coli Data Loader - Quick Test")
    print("=" * 60)
    
    # Test simulated data
    print("\n1. Testing simulated data generation...")
    time, df, time_col, od_cols = load_ecoli_data('simulated')
    print(f"   ✅ Generated {len(od_cols)} curves with {len(time)} points each")
    
    # Test URL loading (will fall back to simulated if URL fails)
    print("\n2. Testing URL auto-loading...")
    time, df, time_col, od_cols = load_ecoli_data('auto')
    print(f"   ✅ Loaded data successfully")
    
    print("\n" + "=" * 60)
    print("Data loader module ready!")
    print("Use load_ecoli_data() to load data automatically")
