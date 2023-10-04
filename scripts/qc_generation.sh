#!/bin/bash
#
#     
# Functionality: Generates qc reports for already existing images and their corresponding segmentations/labels     
# Usage:
#   sct_run_batch -script qc_generation.sh --path-data PATH_TO_BIDS_DATA --path-output PATH_TO_QC_OUTPUT
# Output: The index.html in the qc folder will have the qc reports for all the subjects in the data.
#
# Authors: Rohan Banerjee

# The following global variables are retrieved from the caller sct_run_batch
# but could be overwritten by uncommenting the lines below:

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

sct_qc -i ${file_bold} -s ${file_bold_seg} -qc ${PATH_DATA}/qc_SITE_NAME -p sct_deepseg_sc


