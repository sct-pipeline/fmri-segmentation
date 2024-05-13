import numpy as np
import nibabel as nib
import os
from scipy.spatial.distance import directed_hausdorff
import argparse

def dice_coefficient(seg1, seg2, smooth = 1):

    intersection = np.sum(seg1[seg2==1])
    union = np.sum(seg1) + np.sum(seg2)
    if union == 0:
        return 1.0
    else:
        return 2.0 * intersection / union
    
def hausdorff_distance_calc(seg1, seg2):
    predicted_coords = np.argwhere(seg1)
    truth_coords = np.argwhere(seg2)

    hausdorff_distance = max(directed_hausdorff(predicted_coords, truth_coords)[0],
                             directed_hausdorff(truth_coords, predicted_coords)[0])

    return hausdorff_distance

# Load the segmentation masks

all_dice = []

def main(predictions_dir, ground_truth_dir, output_file):
    test_files = os.listdir(predictions_dir)
    subjects = [file_name.split('_')[0] for file_name in test_files]

    all_dice = []

    for i in range(len(subjects)):
        mask1 = nib.load(os.path.join(predictions_dir, subjects[i] + "_task-rest_bold_class-0_pred.nii.gz"))
        mask2 = nib.load(os.path.join(ground_truth_dir, subjects[i], "func", subjects[i] + "_task-pain_desc-spinalcord_mask.nii.gz"))

        data1 = mask1.get_fdata()
        data2 = mask2.get_fdata()

        dice1_2 = dice_coefficient(data2, data1)
        all_dice.append(dice1_2*100)

    np.savetxt(output_file, all_dice, delimiter=",")
    print(all_dice)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Dice Coefficients.')
    parser.add_argument('--predictions_dir', type=str, required=True, help='Directory where the predictions are stored')
    parser.add_argument('--ground_truth_dir', type=str, required=True, help='Directory where the ground truth masks are stored')
    parser.add_argument('--output_file', type=str, required=True, help='Output file to save the Dice coefficients')
    args = parser.parse_args()

    main(args.predictions_dir, args.ground_truth_dir, args.output_file)
