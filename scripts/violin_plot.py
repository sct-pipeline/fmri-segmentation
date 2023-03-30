'''
Write a script to get a specific column from three csv files and generate a violin plot using it
Usage:
1. Change the file_name variable with the csv file that has the test dice scores
2. Run the script using: python violin_plot.py
'''


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd


def get_column(filename, column):
    with open(filename, 'r') as f:
        return [line.split(',')[column] for line in f.readlines()]
file_name = "evaluation_3Dmetrics.csv"

# import sys
# if len(sys.argv) != 1:
#     print('Usage: {} file1'.format(sys.argv[0]))
#     sys.exit(1)
data1 = get_column(file_name, 5)
print(data1)
# data2 = get_column('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/results/20230227_2d_geneva_rest_with_weights/results_eval/evaluation_3Dmetrics.csv', 5)
# data3 = get_column(sys.argv[3], 5)
# data4 = get_column(sys.argv[4], 5)
# data5 = get_column(sys.argv[5], 5)
# data6 = get_column(sys.argv[6], 5)
# data7 = get_column(sys.argv[7], 5)
# data8 = get_column(sys.argv[8], 5)


data = {
    'csf_with_sc_pre-trained': data1[1:]
    # 'geneva rest with pre-trained weights': data2[1:],
    # 'set3(3-4)': data3[1:],
    # 'set4(3-6)': data4[1:],
    # 'set5(4-4)': data5[1:],
    # 'set6(4-6)': data6[1:],
    # 'set7(5-4)': data7[1:],
    # 'set8(5-6)': data8[1:]
}

df = pd.DataFrame(data)
df_long = df.melt(value_vars=['csf_with_sc_pre-trained'], var_name='set', value_name='dice')
df_long['set'] = pd.Categorical(df_long['set'])
df_long['dice'] = pd.to_numeric(df_long['dice'])

print(df_long)

fig, ax = plt.subplots(figsize=(15, 6))
sns.set_theme(style="whitegrid")
sns.violinplot(ax=ax,
               data=df_long,
               x='set',
               y='dice',
               x_order=df_long['set'].cat.codes
               
)
ax.set(xlabel='', ylabel='')
sns.despine()
plt.tight_layout()
plt.title('Test dice score distributions')
plt.xlabel('Dice score distribution') 
plt.ylabel('Test dice score') 
plt.savefig('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/plots/temp__violin.png')
