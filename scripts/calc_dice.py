import numpy as np
import nibabel as nib
import tensorflow.keras.backend as K 
import os

# mention the directory where the predictions are stored
test_files = os.listdir('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_leipzig_pain/leipzig-pain_predictions/')

subjects = [file_name.split('_')[0] for file_name in test_files]

def dice_coefficient(seg1, seg2, smooth = 1):
    # y_truef=K.flatten(seg1)
    # y_predf=K.flatten(seg2)
    # intersection = K.sum(y_truef* y_predf)
    # return((2* intersection + smooth) / (K.sum(y_truef) + K.sum(y_predf) + smooth))

    intersection = np.sum(seg1[seg2==1])
    union = np.sum(seg1) + np.sum(seg2)
    if union == 0:
        return 1.0
    else:
        return 2.0 * intersection / union

# Load the segmentation masks

all_dice = []

for i in range(len(subjects)):

    # mask1 is the prediction
    mask1 = nib.load("/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_leipzig_pain/leipzig-pain_predictions/" + subjects[i] + "_task-rest_bold_class-0_pred.nii.gz")

    # mask2 is the ground truth
    mask2 = nib.load("/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_leipzig_pain/derivatives/label/" + subjects[i] + "/func/" + subjects[i] + "_task-pain_desc-spinalcord_mask.nii.gz")


    # Get the data arrays for the masks
    data1 = mask1.get_fdata()
    data2 = mask2.get_fdata()

    # Calculate the Dice coefficients
    dice1_2 = dice_coefficient(data2, data1)
    all_dice.append(dice1_2*100)


    # write a numpy array as a columnin a csv file, with column name as dice
np.savetxt("/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_leipzig_pain/deepsegvspreds_dice.csv", all_dice, delimiter=",")

    # Print the results
print(all_dice)
