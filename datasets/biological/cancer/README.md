# Cancer Growth Validation - RAP Framework

## Overview

Testing the Recursive Attractor Principle (RAP) on cancer/tumor growth dynamics to validate the universal 85% convergence hypothesis across eukaryotic systems.

## Hypothesis

If RAP is universal, cancer growth should exhibit:
1. **50% bifurcation point** - Transition from exponential to constrained growth
2. **85% attractor lock** - Convergence to 85% of vascular carrying capacity
3. **15% reserve capacity** - Overhead for metastatic potential and adaptation
4. **Superior fit vs Gompertz** - RAP should outperform standard tumor growth models

## Data Sources

### Recommended Public Datasets

1. **Cancer Cell Line Encyclopedia (CCLE)**
   - URL: https://sites.broadinstitute.org/ccle/
   - Contains: Growth rates for 1000+ cancer cell lines
   - Format: Time-series cell counts

2. **NCI-60 Cell Line Panel**
   - URL: https://dtp.cancer.gov/discovery_development/nci-60/
   - Contains: 60 cancer cell lines, growth inhibition data
   - Format: Multiple time points, dose-response curves

3. **Xenograft Tumor Growth Data**
   - Mouse models with implanted human tumors
   - Tumor volume measurements over time
   - Available through publications and supplementary data

4. **The Cancer Genome Atlas (TCGA)**
   - URL: https://www.cancer.gov/tcga
   - Contains: Clinical data including tumor sizes at diagnosis
   - Format: Patient cohorts, longitudinal when available

### Data Requirements

For RAP validation, we need:
- **Time-series data**: Tumor volume/cell count over time
- **Multiple measurements**: At least 20+ time points per curve
- **Carrying capacity**: Maximum tumor size or saturation point
- **Multiple samples**: 100+ independent growth curves (like E. coli validation)

## Expected Results

Based on E. coli validation (99.85% convergence to 85%):

| Metric | E. coli Result | Cancer Prediction |
|--------|---------------|-------------------|
| Convergence to 85% | 99.85% | >95% |
| Mean final utilization | 85.8% ± 0.8% | ~85% ± 2% |
| Bifurcation point | ~50% | ~50% |
| RAP vs baseline | 17% better | >10% better than Gompertz |

## Methodology

### 1. Data Collection
- Download growth curves from public databases
- Extract time-series tumor volume or cell count data
- Normalize to carrying capacity (K) for each curve

### 2. Model Fitting
- Fit RAP model: `dP/dt = r * P * (1 - P/K) * f(P/K)` with snap dynamics
- Fit Gompertz model (standard): `dP/dt = r * P * ln(K/P)`
- Compare fit quality (SSE, R², AIC)

### 3. Convergence Analysis
- Calculate final utilization: `P_final / K`
- Check convergence to 85% (within 5% tolerance)
- Identify bifurcation point (50% utilization)
- Count stable points near attractor

### 4. Cross-Validation
- Test across multiple cancer types (breast, lung, colon, melanoma, etc.)
- Compare in vitro (cell lines) vs in vivo (xenografts)
- Check consistency of 85% attractor across types

## Key Differences from Bacterial Growth

| Feature | Bacteria (Prokaryotic) | Cancer (Eukaryotic) |
|---------|----------------------|---------------------|
| Doubling time | 20-30 min | 12-48 hours |
| Carrying capacity | Nutrient limited | Vascular limited |
| Growth phases | Lag-Log-Stationary | Avascular-Angiogenic-Plateau |
| Complexity | Single cell | Multicellular tissue |
| Expected attractor | 85% (validated ✅) | 85% (testing 🔄) |

## Biological Interpretation

If cancer locks at 85%:
- **15% reserve** enables metastatic potential
- Tumor maintains adaptation capacity
- Explains why tumors rarely fill 100% of vascular supply
- Optimal balance: growth vs resource scarcity response

## File Structure

```
cancer/
├── data/               # Raw growth curve data (add downloaded datasets here)
├── processed/          # Cleaned, normalized data
├── results/           # Fitting results and analysis
├── plots/             # Visualizations
├── cancer_loader.py   # Data loading utilities
├── fit_cancer.py      # Model fitting script
└── README.md          # This file
```

## Getting Started

### Step 1: Download Data
Choose a dataset from above and download to `data/` folder.

### Step 2: Load and Process
```python
from cancer_loader import load_cancer_data

# Load growth curves
time, volumes, metadata = load_cancer_data('data/your_dataset.csv')
```

### Step 3: Fit RAP Model
```python
from core.fitting import fit_rap_curve

# Fit to each tumor growth curve
results = []
for tumor_id, volume_data in volumes.items():
    result = fit_rap_curve(time, volume_data, curve_name=tumor_id)
    results.append(result)
```

### Step 4: Analyze Results
```python
# Check convergence statistics
convergence_rate = sum(r['converged'] for r in results) / len(results)
mean_utilization = np.mean([r['final_util'] for r in results])

print(f"Convergence to 85%: {convergence_rate*100:.1f}%")
print(f"Mean final utilization: {mean_utilization:.3f}")
```

## Status

🔄 **In Progress** (November 2025)

- [x] Folder structure created
- [ ] Data sources identified
- [ ] Data downloaded
- [ ] Loading utilities written
- [ ] RAP model fitted to cancer data
- [ ] Results compared to Gompertz baseline
- [ ] Cross-cancer-type validation
- [ ] Publication-ready figures

## Questions?

Open an issue on GitHub: https://github.com/shackled99/RAP-validation/issues

---

**If RAP holds in cancer, we'll have validated across:**
- 🤖 AI (LLM recursion depth - origin of discovery)
- 🦠 Prokaryotes (E. coli - 99.85% validation ✅)
- 🧬 Eukaryotes (Cancer - testing 🔄)
- 🌌 Cosmology (Flywheel - mathematical framework 📐)

Universal principle status: **pending cancer validation** 🎯
