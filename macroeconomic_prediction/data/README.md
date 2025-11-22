# Data Directory

This folder contains all raw data used for quarterly tracking of the macroeconomic prediction.

## Structure

```
data/
├── quarterly/          # Quarterly snapshots
│   ├── 2025-Q4/       # Baseline data
│   ├── 2026-Q1/       # First update
│   └── ...
├── sources/           # Data source documentation
└── archive/           # Historical revisions (for transparency)
```

## Data Sources

### Primary Sources

1. **IMF World Economic Outlook** - https://www.imf.org/en/Publications/WEO
2. **BIS Global Credit Statistics** - https://www.bis.org/statistics/
3. **World Bank Global Development Indicators** - https://data.worldbank.org/
4. **OECD Fiscal Balance Database** - https://data.oecd.org/

### Update Schedule

- **Quarterly updates**: First week of each quarter end (March 31, June 30, Sept 30, Dec 31)
- **Annual reviews**: Full year analysis each December 31
- **Real-time monitoring**: Crisis indicators tracked continuously

## File Naming Convention

```
YYYY-QX-metric-name.csv
```

Examples:
- `2025-Q4-debt-to-gdp.csv`
- `2026-Q1-policy-indicators.csv`
- `2026-Q2-crisis-indicators.csv`

## Data Integrity

All data files are:
- Timestamped with collection date
- Source-attributed
- Version-controlled (Git tracks all changes)
- Never deleted (moved to archive if superseded)

This ensures:
- ✅ Reproducibility
- ✅ Transparency
- ✅ No retroactive data manipulation
- ✅ Clear audit trail

## Contributing Data

If you have access to additional data sources:

1. Fork the repository
2. Add data files following naming convention
3. Document source in `/sources/`
4. Submit pull request with explanation

All contributions must include:
- Data source URL
- Collection date
- Methodology notes
- Any known limitations

---

**Data collection begins: Q4 2025 (November 22, 2025)**
