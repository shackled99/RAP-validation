"""Universal Data Loader - See AUTOMATION_GUIDE.md for details"""
import os
import json
import glob
import pandas as pd
import numpy as np
from pathlib import Path

class UniversalDataLoader:
    def __init__(self, config_path='config/datasets.json'):
        # Get the directory where this script is located
        self.base_dir = Path(__file__).parent.parent.resolve()
        
        # Make config path absolute
        if not os.path.isabs(config_path):
            config_path = self.base_dir / config_path
        
        self.config_path = config_path
        self.configs = self._load_configs()
    
    def _load_configs(self):
        with open(self.config_path, 'r') as f:
            configs = json.load(f)
        return {k: v for k, v in configs.items() if not k.startswith('_')}
    
    def list_available_datasets(self):
        print("\n" + "="*70)
        print("📁 AVAILABLE DATASETS")
        print("="*70)
        for dataset_id, config in self.configs.items():
            print(f"\n{dataset_id}:")
            print(f"  Name: {config['name']}")
            print(f"  Organism: {config.get('organism', 'Unknown')}")
            print(f"  Expected curves: {config.get('n_curves', 'Unknown')}")
            print(f"  Location: {config['data_directory']}")
        print("="*70 + "\n")
    
    def load_dataset(self, dataset_id, max_files=None):
        if dataset_id not in self.configs:
            raise ValueError(f"Dataset '{dataset_id}' not found")
        
        config = self.configs[dataset_id]
        print(f"\n{'='*70}")
        print(f"📂 LOADING: {config['name']}")
        print(f"{'='*70}")
        
        # Make data directory path absolute
        data_dir = config['data_directory']
        if not os.path.isabs(data_dir):
            data_dir = self.base_dir / data_dir
        
        # Build full pattern path
        pattern_path = os.path.join(data_dir, config['file_pattern'])
        print(f"Looking for files: {pattern_path}")
        
        files = glob.glob(str(pattern_path))
        if not files:
            raise FileNotFoundError(f"No files found matching: {pattern_path}")
        
        if max_files:
            files = files[:max_files]
        
        print(f"Found {len(files)} file(s)")
        
        all_data = []
        for idx, filepath in enumerate(files, 1):
            print(f"  [{idx}/{len(files)}] {os.path.basename(filepath)}...", end='')
            try:
                df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
                time_col = self._find_column(df, config['time_column_patterns'])
                if not time_col:
                    print(" ⚠️ No time column")
                    continue
                
                time_data = df[time_col].values
                od_cols = self._find_columns(df, config['od_column_patterns'], exclude=[time_col])
                if not od_cols:
                    print(" ⚠️ No OD columns")
                    continue
                
                file_id = os.path.basename(filepath).replace('.xlsx', '').replace('.csv', '')
                renamed_cols = {col: f"{file_id}_{col}" for col in od_cols}
                df_subset = df[od_cols].rename(columns=renamed_cols)
                all_data.append({'time': time_data, 'data': df_subset, 'file': filepath})
                print(f" ✅ {len(od_cols)} curves")
            except Exception as e:
                print(f" ❌ {str(e)}")
        
        if not all_data:
            raise RuntimeError("No data loaded")
        
        min_length = min(len(d['time']) for d in all_data)
        reference_time = all_data[0]['time'][:min_length]
        combined_df = pd.DataFrame()
        for d in all_data:
            combined_df = pd.concat([combined_df, d['data'].iloc[:min_length]], axis=1)
        
        print(f"\n✅ Loaded {len(combined_df.columns)} curves")
        return {
            'time': reference_time,
            'data': combined_df,
            'metadata': config,
            'curves': list(combined_df.columns)
        }
    
    def _find_column(self, df, patterns):
        for col in df.columns:
            for pattern in patterns:
                if pattern.lower() in str(col).lower():
                    return col
        return None
    
    def _find_columns(self, df, patterns, exclude=None):
        exclude = exclude or []
        matching = []
        for col in df.columns:
            if col in exclude:
                continue
            for pattern in patterns:
                if pattern.lower() in str(col).lower():
                    matching.append(col)
                    break
        return matching

def load_dataset(dataset_id, max_files=None):
    return UniversalDataLoader().load_dataset(dataset_id, max_files)

def list_datasets():
    UniversalDataLoader().list_available_datasets()
