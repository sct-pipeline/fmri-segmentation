#!/bin/bash
#
#     
# Functionality: Generates qc reports for already existing images and their corresponding segmentations/labels     
# Usage:
#   sct_run_batch -script qc_generation.sh
# Output: The index.html in the qc folder will have the qc reports for all the subjects in the data.
#
# Authors: Rohan Banerjee

# The following global variables are retrieved from the caller sct_run_batch
# but could be overwritten by uncommenting the lines below:
PATH_DATA_PROCESSED="/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/data_Zurich_Lumbar_Rest_bids"
PATH_RESULTS="/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/data_Zurich_Lumbar_Rest_bids/code/results"
PATH_LOG="/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/data_Zurich_Lumbar_Rest_bids/code/log"
PATH_QC="/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/datasets/data_Zurich_Lumbar_Rest_bids/code/qc"

# Uncomment for full verbose
set -x

# Exit if user presses CTRL+C (Linux) or CMD+C (OSX)
trap "echo Caught Keyboard Interrupt within script. Exiting now.; exit" INT

# Print retrieved variables from sct_run_batch to the log (to allow easier debug)
echo “Retrieved variables from from the caller sct_run_batch:”
echo “PATH_DATA: ${PATH_DATA}”
echo “PATH_DATA_PROCESSED: ${PATH_DATA_PROCESSED}”
echo “PATH_RESULTS: ${PATH_RESULTS}”
echo “PATH_LOG: ${PATH_LOG}”
echo “PATH_QC: ${PATH_QC}”

# Retrieve input params
SUBJECT=$1

# echo SUBJECT

# Save script path
PATH_SCRIPT=$PWD

get starting time:
start=`date +%s`

# SCRIPT STARTS HERE
# ==============================================================================
# Display useful info for the log, such as SCT version, RAM and CPU cores available
sct_check_dependencies -short

cd ${SUBJECT}/func
file_bold=${PATH_DATA}/${SUBJECT}/func/${SUBJECT}_task-rest_bold.nii.gz
file_bold_seg=${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_task-rest_bold_seg-manual.nii.gz

echo "file_bold: ${file_bold}"

sct_qc -i ${file_bold} -s ${file_bold_seg} -qc qc -qc-subject ${SUBJECT}


