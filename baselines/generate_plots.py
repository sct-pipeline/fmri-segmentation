"""
Generate plots for the results of the models
Note: Very initial script, WIP

To-do:
1. Write classes
2. Add arguements

Author: Rohan Banerjee
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

csv_files = ['/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/held-out_test_common_bids_resunet/results_resunet.csv', '/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/held-out_test_common_bids_all_manual_data/results_all_manual.csv', '/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/held-out_test_common_bids/results_contrast_agnostic.csv']

dice_scores = []
hausdorff_distances = []
models = []

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df = df[df.iloc[:, 0].str.contains("sub-")]

    dice_scores.extend(df['Dice Score (Mean ± Std Dev)'].str.split('\\+\\-').str[0].astype(float))
    hausdorff_distances.extend(df['Hausdorff Distance (Mean ± Std Dev)'].str.split('\\+\\-').str[0].astype(float))

    model_name = os.path.basename(csv_file).replace('.csv', '')
    models.extend([model_name]*len(df))


df_plot = pd.DataFrame({'Model': models, 'Dice Score': dice_scores, 'Hausdorff Distance': hausdorff_distances})


plt.figure(figsize=(10, 6))
sns.violinplot(x='Model', y='Dice Score', data=df_plot, hue='Model')
plt.savefig('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/plots/test_d_multiple.png')

plt.figure(figsize=(10, 6))
sns.violinplot(x='Model', y='Hausdorff Distance', data=df_plot, hue='Model')
plt.savefig('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/plots/test_h_multiple.png') 