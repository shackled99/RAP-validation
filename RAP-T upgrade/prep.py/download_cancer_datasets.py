"""
Cancer Dataset Downloader
==========================

Automatically downloads cancer cell line growth datasets.

Run this script to download all cancer datasets.

Author: The Potato Researcher 🥔
Date: November 2025
"""

import urllib.request
import os
from pathlib import Path

# Create data directories
base_dir = Path("datasets/cancer")
base_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("CANCER DATASET DOWNLOADER")
print("="*70)

datasets = {
    "HL-60 Leukemia Growth Curves": {
        "url": "https://figshare.com/ndownloader/files/30947966",
        "filename": "hl60_growth.csv",
        "description": "Time-series growth data for HL-60 leukemia cells"
    },
    "DepMap Sample Info": {
        "url": "https://figshare.com/ndownloader/files/48890425",
        "filename": "depmap_sample_info.csv",
        "description": "Doubling times for 1,700+ cancer cell lines"
    },
    "NCI-60 Growth Data": {
        "url": "https://wiki.nci.nih.gov/download/attachments/embedded-page/NCIDTPdata/NCI-60%20Growth%20Inhibition%20Data/nci60gi50.zip?api=v2",
        "filename": "nci60_growth.zip",
        "description": "Growth data for 60 cancer cell lines"
    }
}

for name, info in datasets.items():
    print(f"\n{name}")
    print("-" * 70)
    print(f"Description: {info['description']}")
    
    output_path = base_dir / info['filename']
    
    if output_path.exists():
        print(f"✅ Already exists: {output_path}")
        print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
        continue
    
    print(f"📥 Downloading from: {info['url']}")
    print(f"   Saving to: {output_path}")
    
    try:
        urllib.request.urlretrieve(info['url'], output_path)
        size = output_path.stat().st_size / 1024
        print(f"✅ Downloaded successfully! ({size:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        print(f"   Manual download: {info['url']}")
        print(f"   Save as: {output_path}")

print("\n" + "="*70)
print("DOWNLOAD SUMMARY")
print("="*70)

for name, info in datasets.items():
    output_path = base_dir / info['filename']
    if output_path.exists():
        print(f"✅ {name}: {output_path}")
    else:
        print(f"❌ {name}: MISSING - download manually from:")
        print(f"   {info['url']}")

print("\n" + "="*70)
print("Next steps:")
print("1. Check datasets/cancer/ for downloaded files")
print("2. Run: python prepare_cancer_data.py")
print("3. Load in explorer or batch processor")
print("="*70)
