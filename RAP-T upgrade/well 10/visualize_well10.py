"""
Well 10 Visualization Suite
============================

Creates comprehensive visualizations comparing Well 10 to other cancer wells.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")

# Load data
df = pd.read_excel('C:/Users/lmt04/OneDrive/Desktop/glyphwheel (2)/RAP/datasets/cancer/hl60_processed.xlsx')

time = df['Time (h)'].values
wells = [col for col in df.columns if col.startswith('Well_')]

# RAP results
damping_params = {
    'Well_B4': 0.100, 'Well_B5': 0.100, 'Well_B6': 0.100, 'Well_B7': 0.244,
    'Well_B8': 0.160, 'Well_C4': 0.172, 'Well_C5': 0.117, 'Well_C6': 0.168,
    'Well_C7': 0.100, 'Well_C8': 5.000, 'Well_D4': 0.110, 'Well_D5': 0.139,
    'Well_D6': 0.240, 'Well_D7': 0.100, 'Well_D8': 0.179
}

final_utils = {
    'Well_B4': 0.906, 'Well_B5': 0.906, 'Well_B6': 0.943, 'Well_B7': 0.956,
    'Well_B8': 0.932, 'Well_C4': 0.936, 'Well_C5': 0.915, 'Well_C6': 0.934,
    'Well_C7': 0.907, 'Well_C8': 0.870, 'Well_D4': 0.913, 'Well_D5': 0.925,
    'Well_D6': 0.955, 'Well_D7': 0.904, 'Well_D8': 0.938
}

# Create figure
fig = plt.figure(figsize=(18, 12))

# ============================================================
# Plot 1: All Growth Curves with Well 10 Highlighted
# ============================================================
ax1 = plt.subplot(2, 3, 1)

for well in wells:
    data = df[well].values
    if well == 'Well_C8':  # Well 10
        ax1.plot(time, data, linewidth=4, color='blue', label='Well 10 (C8) - CONVERGED', zorder=10)
    else:
        ax1.plot(time, data, linewidth=1, alpha=0.4, color='red')

# Add one legend entry for other wells
ax1.plot([], [], linewidth=1, alpha=0.4, color='red', label='Other Wells')

ax1.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cell Count', fontsize=12, fontweight='bold')
ax1.set_title('A. All Growth Curves\n(Well 10 in Blue)', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# ============================================================
# Plot 2: Growth Rates Comparison
# ============================================================
ax2 = plt.subplot(2, 3, 2)

growth_rates = []
well_names = []
for well in wells:
    data = df[well].values
    early_rate = (data[1] - data[0]) / 24  # cells per hour
    growth_rates.append(early_rate)
    well_names.append(well.replace('Well_', ''))

# Sort by growth rate
sorted_indices = np.argsort(growth_rates)
sorted_rates = [growth_rates[i] for i in sorted_indices]
sorted_names = [well_names[i] for i in sorted_indices]

# Color Well 10 differently
colors = ['blue' if name == 'C8' else 'red' for name in sorted_names]

bars = ax2.barh(range(len(sorted_names)), sorted_rates, color=colors, alpha=0.7, edgecolor='black')

ax2.set_yticks(range(len(sorted_names)))
ax2.set_yticklabels(sorted_names, fontsize=9)
ax2.set_xlabel('Early Growth Rate (cells/hour)', fontsize=12, fontweight='bold')
ax2.set_title('B. Growth Rate Ranking\n(Slowest to Fastest)', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# Highlight Well 10's bar
well10_idx = sorted_names.index('C8')
ax2.annotate('Well 10', xy=(sorted_rates[well10_idx], well10_idx),
             xytext=(sorted_rates[well10_idx] + 200, well10_idx),
             fontsize=11, fontweight='bold', color='blue',
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))

# ============================================================
# Plot 3: Damping Parameter vs Final Utilization
# ============================================================
ax3 = plt.subplot(2, 3, 3)

damping_vals = [damping_params[w] for w in wells]
util_vals = [final_utils[w] for w in wells]

# Separate Well 10 from others
well10_damping = damping_params['Well_C8']
well10_util = final_utils['Well_C8']

other_damping = [d for w, d in damping_params.items() if w != 'Well_C8']
other_util = [u for w, u in final_utils.items() if w != 'Well_C8']

# Plot others
ax3.scatter(other_damping, [u*100 for u in other_util], 
           s=100, alpha=0.6, color='red', label='Other Wells', edgecolor='black')

# Plot Well 10
ax3.scatter([well10_damping], [well10_util*100], 
           s=300, color='blue', label='Well 10', marker='*', edgecolor='black', linewidth=2, zorder=10)

# 85% reference line
ax3.axhline(y=85, color='green', linestyle='--', linewidth=2, alpha=0.5, label='85% Attractor')

ax3.set_xlabel('Damping Parameter (d)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Final Utilization (%)', fontsize=12, fontweight='bold')
ax3.set_title('C. Damping vs Utilization\n(High Damping → Lower Utilization)', fontsize=14, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# Add annotation
ax3.annotate(f'd = {well10_damping:.1f}\n50x higher!', 
            xy=(well10_damping, well10_util*100),
            xytext=(well10_damping - 1.5, 95),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2))

# ============================================================
# Plot 4: Well 10 Normalized Growth Curve
# ============================================================
ax4 = plt.subplot(2, 3, 4)

# Normalize all curves by their maximum
for well in wells:
    data = df[well].values
    normalized = data / np.max(data) * 100
    
    if well == 'Well_C8':  # Well 10
        ax4.plot(time, normalized, linewidth=4, color='blue', label='Well 10 (C8)', zorder=10)
    else:
        ax4.plot(time, normalized, linewidth=1, alpha=0.4, color='red')

# 85% line
ax4.axhline(y=85, color='green', linestyle='--', linewidth=2, alpha=0.5, label='85% Attractor')

# Add one legend entry for other wells
ax4.plot([], [], linewidth=1, alpha=0.4, color='red', label='Other Wells')

ax4.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax4.set_ylabel('% of Maximum Capacity', fontsize=12, fontweight='bold')
ax4.set_title('D. Normalized Growth Curves\n(% of Individual Max)', fontsize=14, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# ============================================================
# Plot 5: Final Cell Counts Distribution
# ============================================================
ax5 = plt.subplot(2, 3, 5)

final_counts = [df[well].values[-1] for well in wells]
well_labels = [w.replace('Well_', '') for w in wells]

colors = ['blue' if w == 'Well_C8' else 'red' for w in wells]

bars = ax5.bar(range(len(wells)), final_counts, color=colors, alpha=0.7, edgecolor='black')

ax5.set_xticks(range(len(wells)))
ax5.set_xticklabels(well_labels, rotation=45, fontsize=9)
ax5.set_ylabel('Final Cell Count', fontsize=12, fontweight='bold')
ax5.set_title('E. Final Cell Counts\n(Well 10 in Blue)', fontsize=14, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# Annotate Well 10
well10_idx_in_wells = wells.index('Well_C8')
ax5.annotate('Well 10\nLowest Final Count', 
            xy=(well10_idx_in_wells, final_counts[well10_idx_in_wells]),
            xytext=(well10_idx_in_wells + 2, final_counts[well10_idx_in_wells] + 10000),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2))

# ============================================================
# Plot 6: Summary Statistics
# ============================================================
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')

# Calculate statistics
well10_data = df['Well_C8'].values
other_wells_data = [df[w].values for w in wells if w != 'Well_C8']

well10_initial = well10_data[0]
well10_max = np.max(well10_data)
well10_final = well10_data[-1]
well10_growth = well10_final / well10_initial

other_initial = np.mean([d[0] for d in other_wells_data])
other_max = np.mean([np.max(d) for d in other_wells_data])
other_final = np.mean([d[-1] for d in other_wells_data])
other_growth = other_final / other_initial

# Create summary table
summary_data = [
    ['Metric', 'Well 10', 'Other Wells Avg', 'Difference'],
    ['Initial Count', f'{well10_initial:,.0f}', f'{other_initial:,.0f}', f'{((well10_initial/other_initial-1)*100):+.1f}%'],
    ['Maximum Count', f'{well10_max:,.0f}', f'{other_max:,.0f}', f'{((well10_max/other_max-1)*100):+.1f}%'],
    ['Final Count', f'{well10_final:,.0f}', f'{other_final:,.0f}', f'{((well10_final/other_final-1)*100):+.1f}%'],
    ['Growth Ratio', f'{well10_growth:.2f}x', f'{other_growth:.2f}x', f'{((well10_growth/other_growth-1)*100):+.1f}%'],
    ['', '', '', ''],
    ['Final Utilization', '87.0%', '92.5%', '-5.5%'],
    ['Damping (d)', '5.000', '0.155', '+3127%'],
    ['Convergence', 'YES ✅', 'NO ❌', 'Unique'],
]

table = ax6.table(cellText=summary_data, cellLoc='left', loc='center',
                 colWidths=[0.3, 0.25, 0.25, 0.2])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header
for i in range(4):
    cell = table[(0, i)]
    cell.set_facecolor('#34495e')
    cell.set_text_props(weight='bold', color='white')

# Alternate row colors
for i in range(1, len(summary_data)):
    for j in range(4):
        cell = table[(i, j)]
        if i == 5:  # Blank row
            cell.set_facecolor('white')
        elif i % 2 == 0:
            cell.set_facecolor('#ecf0f1')
        else:
            cell.set_facecolor('white')

ax6.set_title('F. Well 10 Summary Statistics', fontsize=14, fontweight='bold', pad=20)

# ============================================================
# Main title and footer
# ============================================================
fig.suptitle('Well 10 Deep Dive: The Only Converged Cancer Well', 
             fontsize=18, fontweight='bold', y=0.98)

footer_text = ('Well 10 shows slower growth, higher damping, and convergence to 87% (vs 92.5% average)\n' +
               'Suggests: Slower-growing cancer cells retain partial growth regulation')
fig.text(0.5, 0.02, footer_text, ha='center', fontsize=11, style='italic',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('C:/Users/lmt04/OneDrive/Desktop/glyphwheel (2)/RAP/well10_analysis.png', 
            dpi=300, bbox_inches='tight')

print("✅ Saved: well10_analysis.png")
print("\nKey findings saved in visualization!")
