Scripts:
- BIDSify_fMRI_data.py - to bidsify the fMRI data
- calc_dice.py - to calculate the dice score in between different segmentations; generally used for deepseg vs trained model segmentation comparison
- violin_plot.py - used for plotting violin plots of dice score distributions
- nnUNet_inference_time.py - A script which can be used to run inference on a particular dataset and calculate the inference time per subject. The outut of the script is a plot which shows the inference time per subject.