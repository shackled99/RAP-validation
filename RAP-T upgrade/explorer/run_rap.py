"""
RAP Master Automation Script
=============================

Single command to process any dataset:
    python run_rap.py <dataset_id>

Examples:
    python run_rap.py ecoli_round5                    # Test on 50 curves
    python run_rap.py ecoli_full --limit 1000         # Process 1000 curves
    python run_rap.py ecoli_full                       # Process all 13,608 curves
    python run_rap.py my_new_dataset --workers 8      # Use 8 cores

Author: The Potato Researcher 🥔
Date: November 2025
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.automated_processor import AutomatedRAPProcessor
from core.universal_loader import list_datasets


def main():
    """Main automation entry point."""
    
    parser = argparse.ArgumentParser(
        description='Automated RAP Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ecoli_round5                     Process validated 50-curve set
  %(prog)s ecoli_full --limit 1000          Process first 1000 curves
  %(prog)s ecoli_full --workers 8           Use 8 CPU cores
  %(prog)s --list                           Show available datasets
        """
    )
    
    parser.add_argument(
        'dataset',
        nargs='?',
        help='Dataset ID from config/datasets.json'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available datasets and exit'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit processing to first N curves (for testing)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        help='Number of parallel workers (default: CPU count - 1)'
    )
    
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh, ignore existing checkpoint'
    )
    
    parser.add_argument(
        '--checkpoint-interval',
        type=int,
        default=100,
        help='Save checkpoint every N curves (default: 100)'
    )
    
    args = parser.parse_args()
    
    # List mode
    if args.list:
        list_datasets()
        return
    
    # Validate dataset provided
    if not args.dataset:
        parser.print_help()
        print("\n❌ Error: dataset ID required")
        print("\nUse --list to see available datasets")
        sys.exit(1)
    
    # Run automated processing
    print("\n" + "="*70)
    print("🥔 RAP AUTOMATED ANALYSIS PIPELINE")
    print("="*70)
    print(f"Dataset: {args.dataset}")
    
    if args.limit:
        print(f"Limit: {args.limit} curves")
    
    if args.workers:
        print(f"Workers: {args.workers}")
    
    print("="*70 + "\n")
    
    try:
        processor = AutomatedRAPProcessor(
            checkpoint_interval=args.checkpoint_interval
        )
        
        summary = processor.process_dataset(
            dataset_id=args.dataset,
            max_curves=args.limit,
            n_workers=args.workers,
            resume=not args.no_resume
        )
        
        print("\n" + "="*70)
        print("🎉 ANALYSIS COMPLETE!")
        print("="*70)
        
        if 'convergence' in summary:
            conv = summary['convergence']
            print(f"\n✅ Key Result: {conv['convergence_rate_85']*100:.1f}% convergence to 85% attractor")
            print(f"   Mean final utilization: {conv['mean_final_util']:.3f} ± {conv['std_final_util']:.3f}")
        
        print(f"\n📁 Results saved in: results/automated/{args.dataset}/")
        print("="*70 + "\n")
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("  1. Dataset files exist in the configured directory")
        print("  2. Dataset is properly configured in config/datasets.json")
        print("  3. File patterns match actual files")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
