# COMMIT MESSAGE TEMPLATE

## Initial Commit

```
LOCKED PREDICTION: Global debt hard reset 2027-2032

Testing RAP framework at civilizational scale

Key Parameters:
- Starting debt-to-GDP: 235% (IMF 2025)
- Target attractor: 85% (validated across 12,547 biological systems)
- Required damping: d = 10-12 (impossible, 5× biological maximum)
- Current damping: d < 0 (negative, expansionary policy)
- r - g differential: 0.0-1.5% (debt compounds faster than growth)

Prediction:
- 70% probability: Hard reset 2027-2032 via inflation/default/collapse
- 20% probability: Stabilization at 100-120% (attractor inaccessible)
- 10% probability: Other outcomes (framework failure, AGI miracle, etc.)

Falsification Criteria:
- Debt < 90% by 2040 without reset → Framework needs revision
- Debt > 120% by 2040 → Prediction confirmed
- Hard reset 2027-2032 → Timeline and mechanism validated

Prediction locked: November 22, 2025
Next update: Q1 2026 (March 2026)

Files added:
- macroeconomic_prediction/PREDICTION.md (main prediction, LOCKED)
- macroeconomic_prediction/README.md (folder overview)
- macroeconomic_prediction/methodology.md (calculation methods)
- macroeconomic_prediction/quarterly_tracking.md (ongoing updates)
- macroeconomic_prediction/analysis/damping_calculator.py (tools)
- macroeconomic_prediction/data/README.md (data structure)
- Updated main README.md with prediction reference
```

---

## Quarterly Update Template

```
Q[X] 20[YY] update: Actual vs predicted trajectory

Core Metrics:
- Debt-to-GDP: [actual]% (predicted: [predicted]%)
- Effective damping: d = [calculated] ([direction from prior quarter])
- r - g differential: [value]% ([interpretation])
- Primary deficit: [value]% of GDP

Crisis Indicators:
- Bond spreads: [status]
- Sovereign CDS: [status]  
- Currency volatility: [status]
- Overall risk: [LOW/MODERATE/ELEVATED/HIGH/CRITICAL]

Analysis:
- Deviation from prediction: ±[X] percentage points
- [Explanation of any significant deviations]
- [Policy changes and their impact on damping]
- [Any structural surprises or black swans]

Probability Updates:
- Hard reset 2027-2032: [X]% (was Y%)
- [Reasoning for any probability adjustments]

Next update: Q[X+1] 20[YY]
```

---

## File Update Protocol

**For quarterly updates**:
1. Never modify PREDICTION.md (it's locked)
2. Only update quarterly_tracking.md
3. Add new data files to /data/quarterly/
4. Commit with descriptive message following template above

**For methodology refinements**:
1. methodology.md can be updated (document revisions)
2. Clearly note version history at bottom
3. Core prediction in PREDICTION.md remains unchanged

**For code improvements**:
1. Update analysis scripts as needed
2. Maintain backward compatibility
3. Document changes in comments

---

## Git Workflow

### Initial commit (now)
```bash
cd RAP-validation
git add macroeconomic_prediction/
git add README.md
git commit -m "[Use template above]"
git push origin main
```

### Quarterly updates
```bash
cd RAP-validation
git add macroeconomic_prediction/quarterly_tracking.md
git add macroeconomic_prediction/data/quarterly/[YYYY-QX]/
git commit -m "[Use quarterly template above]"
git push origin main
```

### Tag major milestones
```bash
# Initial prediction
git tag -a v1.0-prediction-locked -m "Macroeconomic prediction locked Nov 22 2025"

# First year complete
git tag -a v1.1-year1-complete -m "One year of tracking complete"

# Crisis onset (if occurs)
git tag -a v2.0-reset-triggered -m "Hard reset mechanism activated"

git push origin --tags
```

---

## GitHub Actions (Optional Future Enhancement)

Could automate:
- Quarterly data pulls from IMF/BIS APIs
- Automatic calculation of effective damping
- Alert emails when crisis indicators hit thresholds
- Auto-generation of updated plots

*Not implemented yet, but infrastructure ready*

---

**Prediction Status: LOCKED**  
**Date: November 22, 2025**  
**Next Action: Quarterly update Q1 2026**
