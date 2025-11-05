# E. coli Data Download Instructions

⚠️ **Raw data files not included in this repository due to size (~500MB) and licensing considerations.**

## How to Get the Data

### Step 1: Download from Figshare

**Dataset:** Aida et al. (2025) - *E. coli* BW25113 Growth Profiles  
**DOI:** 10.6084/m9.figshare.28342064  
**Link:** https://figshare.com/articles/dataset/28342064

### Step 2: Download These Files

You need the following Excel files:

1. `BW25113_Growth_Round01.xlsx`
2. `BW25113_Growth_Round02.xlsx`
3. `BW25113_Growth_Round03.xlsx`
4. `BW25113_Growth_Round04.xlsx`
5. `BW25113_Growth_Round05.xlsx`
6. `BW25113_Growth_Round06.xlsx`
7. `BW25113_Growth_Round07.xlsx`
8. `BW25113_GrowthDataEvaluation.xlsx`
9. `BW25113_Medium composition.xlsx`

**Total size:** ~500MB

### Step 3: Place Files in Correct Location

Create this folder structure:
```
RAP-validation/
└── datasets/
    └── biological/
        └── ecoli_data/          ← Create this folder
            ├── BW25113_Growth_Round01.xlsx
            ├── BW25113_Growth_Round02.xlsx
            ├── ... (all 9 files)
```

### Step 4: Run the Tests

```bash
# Test the data loader
python datasets/biological/test_loader.py

# Run full E. coli validation
python tests/test_ecoli.py

# Analyze outliers
python tests/analyze_ecoli_outliers.py
```

---

## Quick Start (Without Downloading Data)

Want to see RAP in action without downloading 500MB?

```bash
# Test on simulated data
python tests/test_rap_detection.py
```

This generates synthetic RAP-compliant data and validates the model.

---

## Data License

The Aida et al. dataset is publicly available on Figshare. Please check their licensing terms before use. Typically Figshare data is CC-BY (attribution required).

**Proper citation:**
```bibtex
@dataset{aida_ecoli_2025,
  title={E. coli BW25113 Growth Profiles in Defined Media},
  author={Aida, et al.},
  year={2025},
  publisher={Figshare},
  doi={10.6084/m9.figshare.28342064}
}
```

---

## Troubleshooting

**"No such file or directory"**
- Make sure files are in `datasets/biological/ecoli_data/`
- Check that folder name is exactly `ecoli_data` (no spaces, correct case)

**"Module not found"**
- Run `pip install -r requirements.txt` from repo root
- Make sure you're using Python 3.11+

**"Permission denied"**
- Check file permissions on downloaded Excel files
- Try running from an administrator terminal (Windows)

---

## Results Without Data

Even without downloading the full dataset, you can:

✅ View our complete analysis (see `results/` folder)  
✅ See summary statistics and plots  
✅ Read outlier analysis report  
✅ Test the RAP model on simulated data  
✅ Use the framework for your own data  

The raw E. coli data is only needed to **replicate** our exact validation, not to use the RAP framework!
