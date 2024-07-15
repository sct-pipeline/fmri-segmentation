"""
Generate plots for the results of the models
Note: Very initial script, WIP (NOT TO BE REVIEWED)

To-do:
1. Write classes
2. Add arguements

Author: Rohan Banerjee
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import ptitprince as pt
import argparse
import matplotlib.patches as mpatches

parser = argparse.ArgumentParser(description='Process results CSV files.')
parser.add_argument('--csv_files', metavar='CSV', type=str, nargs='+')
args = parser.parse_args()
csv_files = args.csv_files

dice_scores = []
hausdorff_distances = []
models = []

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df = df[df.iloc[:, 0].str.contains("sub-")]

    dice_scores.extend(df['Dice Score (Mean ± Std Dev)'].str.split('\\+\\-').str[0].astype(float))
    hausdorff_distances.extend(df['Hausdorff Distance (Mean ± Std Dev)'].str.split('\\+\\-').str[0].astype(float))

    model_name = os.path.basename(csv_file).replace('.csv', '').split('_')[-1]
    models.extend([model_name]*len(df))


df_plot = pd.DataFrame({'Model': models, 'Dice Score': dice_scores, 'Hausdorff Distance': hausdorff_distances})



# Plot Dice Score
plt.figure(figsize=(10, 6))
sns.set_theme(style="darkgrid")
rain = pt.RainCloud(x='Model', y='Dice Score', data=df_plot,palette="Set2", bw=.2, linewidth = 2, width_viol=.7, orient="v", alpha=1.0, point_size = 4, dodge = False, pointplot=True, linecolor = 'purple')

# # Customize legend to show unique model names
# handles, labels = rain.get_legend_handles_labels()
# by_label = dict(zip(labels, handles))
# plt.legend(by_label.values(), by_label.keys(), loc='lower right')

plt.savefig('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/plots/methods_comparison_dice.png', bbox_inches='tight')


# Plot Hausdorff Distance
plt.figure(figsize=(10, 6))
rain = pt.RainCloud(x='Model', y='Hausdorff Distance', data=df_plot,palette="Set2", bw=.2, linewidth = 1, width_viol=.7, orient="v", alpha=1.0, point_size = 4, dodge = False, pointplot=True, linecolor = 'purple')

# Customize legend to show unique model names
handles, labels = rain.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper right')
plt.savefig('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/plots/methods_comparison_hausdorff.png', bbox_inches='tight') 
