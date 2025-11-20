"""Automated Batch RAP Processor - See AUTOMATION_GUIDE.md"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
from core.fitting import fit_rap_curve
from core.universal_loader import load_dataset

class AutomatedRAPProcessor:
    def __init__(self, output_dir='results/automated', checkpoint_interval=100):
        self.output_dir = output_dir
        self.checkpoint_interval = checkpoint_interval
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def process_dataset(self, dataset_id, max_curves=None, n_workers=None, resume=True):
        dataset_dir = os.path.join(self.output_dir, dataset_id)
        Path(dataset_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*70}")
        print(f"🚀 AUTOMATED RAP PROCESSING")
        print(f"{'='*70}")
        
        data = load_dataset(dataset_id)
        time_data = data['time']
        df = data['data']
        curves = data['curves']
        metadata = data['metadata']
        
        if max_curves:
            curves = curves[:max_curves]
        
        checkpoint_path = os.path.join(dataset_dir, 'checkpoint.json')
        if resume and os.path.exists(checkpoint_path):
            with open(checkpoint_path, 'r') as f:
                checkpoint = json.load(f)
            completed = set(checkpoint.get('completed_curves', []))
            curves_to_process = [c for c in curves if c not in completed]
            print(f"♻️  Resuming: {len(completed)} done, {len(curves_to_process)} remaining")
        else:
            completed = set()
            curves_to_process = curves
            checkpoint = {'dataset_id': dataset_id, 'started': timestamp, 'completed_curves': []}
        
        if not curves_to_process:
            print("✅ All curves processed!")
            return self._load_existing_summary(dataset_dir)
        
        if n_workers is None:
            n_workers = max(1, mp.cpu_count() - 1)
        
        print(f"Processing {len(curves_to_process)} curves with {n_workers} workers")
        
        fit_func = partial(self._fit_single_curve, time_data=time_data, df=df)
        results = []
        batch_size = self.checkpoint_interval
        
        for batch_start in range(0, len(curves_to_process), batch_size):
            batch_end = min(batch_start + batch_size, len(curves_to_process))
            batch_curves = curves_to_process[batch_start:batch_end]
            
            if n_workers > 1:
                with mp.Pool(n_workers) as pool:
                    batch_results = list(tqdm(pool.imap(fit_func, batch_curves), total=len(batch_curves)))
            else:
                batch_results = [fit_func(curve) for curve in tqdm(batch_curves)]
            
            results.extend(batch_results)
            completed.update(batch_curves)
            checkpoint['completed_curves'] = list(completed)
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint, f)
            
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(os.path.join(dataset_dir, 'results_temp.csv'), index=False)
        
        results_df = pd.DataFrame(results)
        results_path = os.path.join(dataset_dir, f'results_{timestamp}.csv')
        results_df.to_csv(results_path, index=False)
        
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
        
        return self._generate_summary(results_df, metadata, dataset_dir, timestamp)
    
    def _fit_single_curve(self, curve_name, time_data, df):
        try:
            od_data = df[curve_name].dropna().values
            aligned_time = time_data[:len(od_data)]
            return fit_rap_curve(aligned_time, od_data, curve_name=curve_name, verbose=False)
        except Exception as e:
            return {'curve': curve_name, 'success': False, 'error': str(e)}
    
    def _generate_summary(self, results_df, metadata, dataset_dir, timestamp):
        successful = results_df[results_df['success'] == True]
        
        summary = {
            'dataset': metadata['name'],
            'timestamp': timestamp,
            'total_curves': len(results_df),
            'successful_fits': len(successful),
            'success_rate': len(successful) / len(results_df) if len(results_df) > 0 else 0,
        }
        
        if len(successful) > 0:
            summary['convergence'] = {
                'converged_85': int(successful['converged'].sum()),
                'convergence_rate_85': float(successful['converged'].mean()),
                'mean_final_util': float(successful['final_util'].mean()),
                'std_final_util': float(successful['final_util'].std()),
            }
            
            summary['model_comparison'] = {
                'rap_superior': int(successful['rap_better'].sum()),
                'rap_superiority_rate': float(successful['rap_better'].mean()),
                'mean_improvement': float((successful['sse_logistic'].mean() - successful['sse_rap'].mean()) / successful['sse_logistic'].mean() * 100)
            }
        
        summary_path = os.path.join(dataset_dir, f'summary_{timestamp}.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self._print_summary(summary)
        return summary
    
    def _print_summary(self, summary):
        print(f"\n{'='*70}")
        print(f"📈 SUMMARY: {summary['dataset']}")
        print(f"{'='*70}")
        print(f"Total: {summary['total_curves']}")
        print(f"Successful: {summary['successful_fits']} ({summary['success_rate']*100:.1f}%)")
        
        if 'convergence' in summary:
            conv = summary['convergence']
            print(f"\nConvergence to 85%: {conv['converged_85']}/{summary['successful_fits']} ({conv['convergence_rate_85']*100:.1f}%)")
            print(f"Mean utilization: {conv['mean_final_util']:.3f} ± {conv['std_final_util']:.3f}")
        print(f"{'='*70}\n")
    
    def _load_existing_summary(self, dataset_dir):
        json_files = glob.glob(os.path.join(dataset_dir, 'summary_*.json'))
        if json_files:
            with open(sorted(json_files)[-1], 'r') as f:
                return json.load(f)
        return {}

def process_dataset_auto(dataset_id, max_curves=None, n_workers=None):
    processor = AutomatedRAPProcessor()
    return processor.process_dataset(dataset_id, max_curves=max_curves, n_workers=n_workers)
