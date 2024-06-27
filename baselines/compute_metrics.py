import numpy as np
import nibabel as nib
import os
from scipy.spatial.distance import directed_hausdorff
import argparse
import glob
import statistics
import csv
import matplotlib.pyplot as plt
from scipy import ndimage
import warnings
from medpy.metric import binary

"""
This script calculates the Dice coefficient and the Hausdorff Distance between the predicted segmentation masks and the ground truth masks.
Usage: python get_metrics.py --predictions_dir <PATH_TO_PREDS>    
            --ground_truth_dir <PATH_TO_GT>
             --output_file <PATH_TO_CSV> --pred_suffix <PREDICTION_SUFFIX>

NOTE: The script assumes that the predictions and the ground truth masks are stored in the same directory structure as the one generated by the preprocessing script i.e. in BIDS format.

Example dataset:

├── derivatives
│	 └── labels
│	     ├── sub-001
│	     │	 └── func
│	     │	     ├── sub-001_bold_seg-manual.json
│	     │	     ├── ssub-001_bold_seg-manual.nii.gz
│	     │	     ├── sub-001_bold_seg-sc_epi.json
│	     │	     └── sub-001_bold_seg-sc_epi.nii.gz
│	     ├       └── sub-001_bold_seg-deepseg.json
│	     │       └── sub-001_bold_seg-deepseg.nii.gz
│	     ├       └── sub-001_bold_seg-propseg.json
│	     │       └── sub-001_bold_seg-propseg.nii.gz
│
├── sub-001
│	 └── func
│	     ├── sub-5416_T2w.json
│	     └── sub-5416_T2w.nii.gz


Author: Rohan Banerjee
Metrics adopted from the MetricsReloaded repository (https://github.com/Project-MONAI/MetricsReloaded), credits goes to the authors.
"""

# Below are the older implementations of dice score and hausdorff distance (& simpler). The results match with the current implementation. Using the metrics reloaded implementation for now to have stable implementations for future use.
# def dice_coefficient(seg1, seg2, smooth = 1):
#     intersection = np.sum(seg1[seg2==1])
#     union = np.sum(seg1) + np.sum(seg2)
#     if union == 0:
#         return 1.0
#     else:
#         return 2.0 * intersection / union
    
# def hausdorff_distance_calc(seg1, seg2):
#     predicted_coords = np.argwhere(seg1)
#     truth_coords = np.argwhere(seg2)

#     hausdorff_distance = max(directed_hausdorff(predicted_coords, truth_coords)[0],
#                              directed_hausdorff(truth_coords, predicted_coords)[0])

#     return hausdorff_distance

class MorphologyOps(object):
    """
    Class that performs the morphological operations needed to get notably
    connected component. To be used in the evaluation
    """

    def __init__(self, binary_img, connectivity):
        self.binary_map = np.asarray(binary_img, dtype=np.int8)
        self.connectivity = connectivity

    def border_map(self):
        """
        Create the border map defined as the difference between the original image 
        and its eroded version

        :return: border
        """
        eroded = ndimage.binary_erosion(self.binary_map)
        border = self.binary_map - eroded
        return border

    def border_map2(self):
        """
        Creates the border for a 3D image
        :return:
        """
        west = ndimage.shift(self.binary_map, [-1, 0, 0], order=0)
        east = ndimage.shift(self.binary_map, [1, 0, 0], order=0)
        north = ndimage.shift(self.binary_map, [0, 1, 0], order=0)
        south = ndimage.shift(self.binary_map, [0, -1, 0], order=0)
        top = ndimage.shift(self.binary_map, [0, 0, 1], order=0)
        bottom = ndimage.shift(self.binary_map, [0, 0, -1], order=0)
        cumulative = west + east + north + south + top + bottom
        border = ((cumulative < 6) * self.binary_map) == 1
        return border

    def foreground_component(self):
        return ndimage.label(self.binary_map)

    def list_foreground_component(self):
        labels, _ = self.foreground_component()
        list_ind_lab = []
        list_volumes = []
        list_com = []
        list_values = np.unique(labels)
        for f in list_values:
            if f > 0:
                tmp_lab = np.where(
                    labels == f, np.ones_like(labels), np.zeros_like(labels)
                )
                list_ind_lab.append(tmp_lab)
                list_volumes.append(np.sum(tmp_lab))
                list_com.append(ndimage.center_of_mass(tmp_lab))
        return list_ind_lab, list_volumes, list_com
    


class CalculateMetrics(object):
    def __init__(self, ref, pred, connectivity_type=1, pixdim=None):
        self.ref=ref
        self.pred=pred
        self.connectivity=connectivity_type
        self.pixdim=pixdim

    def n_pos_ref(self):
        """
        Returns the number of elements in ref
        """
        return np.sum(self.ref)
    
    def n_pos_pred(self):
        """
        Returns the number of positive elements in the prediction
        """
        return np.sum(self.pred)
    
    def __tp_map(self):
        """
        This function calculates the true positive map

        :return: TP map
        """
        ref_float = np.asarray(self.ref, dtype=np.float32)
        pred_float = np.asarray(self.pred, dtype=np.float32)
        return np.asarray((ref_float + pred_float) > 1.0, dtype=np.float32)

    def tp(self):
        """
        Returns the number of true positive (TP) elements
        """
        return np.sum(self.__tp_map())
    
    def dsc(self):
        """
        Calculates the Dice Similarity Coefficient defined as

        Lee R Dice. 1945. Measures of the amount of ecologic association between species. Ecology 26, 3 (1945), 297–302.

        ..math::

            DSC = \dfrac{2TP}{2TP+FP+FN}

        This is also F:math:`{\\beta}` for :math:`{\\beta}`=1

        """

        numerator = 2 * self.tp()
        denominator = self.n_pos_pred() + self.n_pos_ref()
        if denominator == 0:
            warnings.warn("Both Prediction and Reference are empty - set to 1 as correct solution even if not defined")
            return 1
        else:
            return numerator / denominator
        
    def border_distance(self):
        """
        This functions determines the map of distance from the borders of the
        prediction and the reference and the border maps themselves

        :return: distance_border_ref, distance_border_pred, border_ref,
        border_pred
        """
        border_ref = MorphologyOps(self.ref, self.connectivity).border_map()
        border_pred = MorphologyOps(self.pred, self.connectivity).border_map()
        oppose_ref = 1 - self.ref
        oppose_pred = 1 - self.pred
        distance_ref = ndimage.distance_transform_edt(
            1 - border_ref, sampling=self.pixdim
        )
        distance_pred = ndimage.distance_transform_edt(
            1 - border_pred, sampling=self.pixdim
        )
        distance_border_pred = border_ref * distance_pred
        distance_border_ref = border_pred * distance_ref

        return distance_border_ref, distance_border_pred, border_ref, border_pred
    
    def measured_distance(self):
        """
        This functions calculates the average symmetric distance and the
        hausdorff distance between a prediction and a reference image

        :return: hausdorff distance and average symmetric distance, hausdorff distance at perc
        and masd
        """
            
        perc = 95
        if np.sum(self.pred + self.ref) == 0:
            return 0, 0, 0, 0
        (
            ref_border_dist,
            pred_border_dist,
            ref_border,
            pred_border,
        ) = self.border_distance()
        #print(ref_border_dist)
        average_distance = (np.sum(ref_border_dist) + np.sum(pred_border_dist)) / (
            np.sum(pred_border + ref_border)
        )
        masd = 0.5 * (
            np.sum(ref_border_dist) / np.sum(pred_border)
            + np.sum(pred_border_dist) / np.sum(ref_border)
        )

        hausdorff_distance = np.max([np.max(ref_border_dist), np.max(pred_border_dist)])

        hausdorff_distance_perc = np.max(
            [
                np.percentile(ref_border_dist[pred_border > 0], q=perc),
                np.percentile(pred_border_dist[ref_border > 0], q=perc),
            ]
        )

        return hausdorff_distance, average_distance, hausdorff_distance_perc, masd
    

    def measured_hausdorff_distance_perc(self):
        """
        This function returns the xth percentile hausdorff distance

        Daniel P Huttenlocher, Gregory A. Klanderman, and William J Rucklidge. 1993. Comparing images using the Hausdorff
        distance. IEEE Transactions on pattern analysis and machine intelligence 15, 9 (1993), 850–863.

        :return: hausdorff_distance_perc
        """
        return self.measured_distance()[2]



def bids_processing(predictions_dir):
    subjects = []
    for root, dirs, files in os.walk(predictions_dir):
        for file in files:
            if file.endswith(".nii.gz"):
                subjects.append(file.split('_')[0])
    
    return list(set(subjects))


def nnunet_processing(predictions_dir):
    test_files = [file_name for file_name in os.listdir(predictions_dir) if file_name.endswith('.nii.gz')]
    test_files = [file_name for file_name in test_files if file_name != '.DS_Store']
    subjects = [file_name.split('_')[0] for file_name in test_files]
    
    return subjects
    


# Load the segmentation masks

all_dice = []

def main(predictions_dir, ground_truth_dir, output_file, pred_suffix, data_type):
    # test_files = [file_name for file_name in os.listdir(predictions_dir) if file_name.endswith('.nii.gz')]
    # test_files = [file_name for file_name in test_files if file_name != '.DS_Store']
    # subjects = [file_name.split('_')[0] for file_name in test_files]

    if data_type == "bids":
        subjects = bids_processing(predictions_dir)
    else:
        subjects = nnunet_processing(predictions_dir)
        print(subjects)
    
    all_dice = []
    all_hausdorff = []

    for i in range(len(subjects)):
        
        if data_type == "bids":
            mask1_files = glob.glob(os.path.join(predictions_dir, subjects[i], "func", subjects[i] + pred_suffix + ".nii.gz"))
            if mask1_files:
                mask1 = mask1_files[0]
                print(f"mask1 found for subject {subjects[i]}")
            else:
                print(f"No mask1 found for subject {subjects[i]}")
                continue

            mask2_files = glob.glob(os.path.join(ground_truth_dir, subjects[i], "func", subjects[i] + "*_seg-manual.nii.gz"))
            if mask2_files:
                mask2 = nib.load(mask2_files[0])
                print(f"mask2 found for subject {subjects[i]}")
            else:
                print(f"No mask2 found for subject {subjects[i]}")
                continue
        else:
            mask1_files = glob.glob(os.path.join(predictions_dir, subjects[i] + "*" + pred_suffix + ".nii.gz"))
            if mask1_files:
                mask1 = mask1_files[0]
                print(f"mask1 found for subject {subjects[i]}")
            else:
                print(f"No mask1 found for subject {subjects[i]}")
                continue

            mask2_files = glob.glob(os.path.join(ground_truth_dir, subjects[i], "func", subjects[i] + "*_seg-manual.nii.gz"))
            # print(os.path.join(ground_truth_dir, subjects[i], "func", subjects[i] + "*_spinalcordmask.nii.gz"))
            if mask2_files:
                mask2 = nib.load(mask2_files[0])
                print(f"mask2 found for subject {subjects[i]}")
            else:
                print(f"No mask2 found for subject {subjects[i]}")
                continue

        # mask1 = os.path.join(predictions_dir, subjects[i],  "func", subjects[i] + pred_suffix + ".nii.gz")
        # mask2_files = glob.glob(os.path.join(ground_truth_dir, subjects[i], "func", subjects[i] + "*_seg-manual.nii.gz"))
        if mask2_files:
            mask2 = nib.load(mask2_files[0])
        else:
            print(f"No mask1 found for subject {subjects[i]}")
            continue
        
        if os.path.exists(mask1) and os.path.getsize(mask1) > 0:
            mask1 = nib.load(mask1)
            data1 = mask1.get_fdata()
            data2 = mask2.get_fdata()

            # dice1_2 = dice_coefficient(data2, data1)
            # hausdorff1_2 = hausdorff_distance_calc(data1, data2)

            metrics = CalculateMetrics(data2, data1)
            # dice1_2 = metrics.dsc()
            dice1_2 = binary.dc(data1, data2)
            all_dice.append(dice1_2)
            hausdorff1_2 = metrics.measured_hausdorff_distance_perc()
            # hausdorff1_2 = binary.hd95(data1, data2)
            all_hausdorff.append(hausdorff1_2)

        else:
            # handle the case where mask1 is not present
            dice1_2 = 0
            hausdorff1_2 = 100

    mean_dice = statistics.mean(all_dice)
    std_dev_dice = statistics.stdev(all_dice)
    mean_hausdorff = statistics.mean(all_hausdorff)
    std_dev_hausdorff = statistics.stdev(all_hausdorff)

    print("Dice: ", statistics.mean(all_dice), statistics.stdev(all_dice))
    print("Hausdorff: ",statistics.mean(all_hausdorff), statistics.stdev(all_hausdorff))

    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        if csvfile.tell() == 0:
        #     writer.writerow(["Ground Truth Filename", "Prediction Filename", "Dice Score", "Hausdorff Distance"])
        # writer.writerow([subjects[i] + "_seg-manual.nii.gz", subjects[i] + pred_suffix + ".nii.gz", dice1_2, hausdorff1_2])
            writer.writerow(["Subject", "Dice Score (Mean ± Std Dev)", "Hausdorff Distance (Mean ± Std Dev)"])
            for i in range(len(subjects)):
                writer.writerow([subjects[i], "{:.2f}".format(all_dice[i]) + "+-" + "{:.2f}".format(std_dev_dice), "{:.2f}".format(all_hausdorff[i]) + "+-" + "{:.2f}".format(std_dev_hausdorff)])
            writer.writerow(["Mean", "{:.2f}".format(mean_dice) + "+-" + "{:.2f}".format(std_dev_dice), "{:.2f}".format(mean_hausdorff) + "+-" + "{:.2f}".format(std_dev_hausdorff)])
        writer.writerow([pred_suffix, "{:.2f}".format(mean_dice) + "+-" + "{:.2f}".format(std_dev_dice), "{:.2f}".format(mean_hausdorff) + "+-" + "{:.2f}".format(std_dev_hausdorff)])

    print(all_dice)
    print(all_hausdorff)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate metrics for your data')
    parser.add_argument('--predictions_dir', type=str, required=True, help='Directory where the predictions are stored')
    parser.add_argument('--ground_truth_dir', type=str, required=True, help='Directory where the ground truth masks are stored')
    parser.add_argument('--output_file', type=str, required=True, help='Output file to save the Dice coefficients')
    parser.add_argument('--pred_suffix', type=str, required=True, help='Suffix of the prediction files')
    parser.add_argument('--data_type', type=str, required=True, help='Suffix of the prediction files')
    args = parser.parse_args()

    main(args.predictions_dir, args.ground_truth_dir, args.output_file, args.pred_suffix, args.data_type)
