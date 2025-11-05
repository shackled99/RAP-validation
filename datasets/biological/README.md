# Biological Datasets

## E. coli Growth Data

**Source:** Aida et al. (2025)  
**Citation:** E. coli BW25113 Growth Profiles in Defined Media  
**DOI:** 10.6084/m9.figshare.28342064  
**Download:** https://figshare.com/articles/dataset/28342064

### Dataset Description

- **Organism:** *Escherichia coli* strain BW25113
- **Media types:** 1,029 chemically defined media
- **Compounds:** 44 pure compounds in various combinations
- **Replicates:** 7 rounds of measurements
- **Time points:** 97 measurements per curve over 48 hours
- **Measurement:** Optical density (OD₆₀₀)

### Files Required

Download these files from Figshare and place in `ecoli_data/` folder:

```
datasets/biological/ecoli_data/
├── BW25113_Growth_Round01.xlsx
├── BW25113_Growth_Round02.xlsx
├── BW25113_Growth_Round03.xlsx
├── BW25113_Growth_Round04.xlsx
├── BW25113_Growth_Round05.xlsx
├── BW25113_Growth_Round06.xlsx
├── BW25113_Growth_Round07.xlsx
├── BW25113_GrowthDataEvaluation.xlsx
└── BW25113_Medium composition.xlsx
```

**Total size:** ~500MB

### Data License

Check Figshare page for licensing terms. Likely CC-BY (attribution required).

### Usage

Once downloaded, run:

```bash
python tests/test_ecoli.py
```

This will:
1. Load all growth curves
2. Fit RAP model to each curve
3. Compare to logistic baseline
4. Generate summary statistics and plots

### Data Quality Notes

The Aida et al. dataset includes:
- **High-quality curves:** Standard growth conditions
- **Edge cases:** Minimal media, toxic conditions
- **Intentional stress tests:** To probe growth limits

Our validation uses ALL curves without pre-filtering (except obvious artifacts), demonstrating model selectivity.

---

## Cancer Growth Data

Coming soon. Will include:
- Mouse xenograft tumor volumes
- Patient tumor tracking data
- Cell culture spheroid growth
- Treatment response dynamics

---

## Additional Datasets

Future validations planned for:
- Yeast growth (*S. cerevisiae*)
- Viral dynamics
- Other prokaryotic species

---

**Note:** Raw data files are not included in this repository due to size and licensing. Users must download from original sources.
