#!/bin/bash

# This script runs inference on the dataset on the BIDS datasets using the sct seg_sc_epi model, sct_deepseg_sc and the sct_propseg model. The outputs of the models are saved in the derivatives folders with the following suffixes:
# sct_epi_seg --> _sct_epi_seg
# sct_deepseg_sc --> _sct_deepseg_sc
# sct_propseg --> _sct_propseg

# Usage: sct_run_batch -config config.json

# Author: Rohan Banerjee

# Uncomment for full verbose
set -x

# Immediately exit if error
set -e -o pipefail

# Exit if user presses CTRL+C (Linux) or CMD+C (OSX)
trap "echo Caught Keyboard Interrupt within script. Exiting now.; exit" INT

# Print retrieved variables from the sct_run_batch script to the log (to allow easier debug)
echo "Retrieved variables from from the caller sct_run_batch:"
echo "PATH_DATA: ${PATH_DATA}"
echo "PATH_DATA_PROCESSED: ${PATH_DATA_PROCESSED}"
echo "PATH_RESULTS: ${PATH_RESULTS}"
echo "PATH_LOG: ${PATH_LOG}"
echo "PATH_QC: ${PATH_QC}"

# Retrieve input params
SUBJECT=$1
echo "SUBJECT: ${SUBJECT}"


# Save script path
PATH_SCRIPT=$PWD

# get starting time:
# start=`date +%s`

# SCRIPT STARTS HERE
# ==============================================================================
# Display useful info for the log, such as SCT version, RAM and CPU cores available
sct_check_dependencies -short

file_bold=${PATH_DATA}/${SUBJECT}/func/${SUBJECT}_task-*.nii.gz

# For running inference using sct seg_sc_epi model on the BIDS data
sct_deepseg -task seg_sc_epi -i ${file_bold} -o ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-sc_epi.nii.gz

# Create JSON file with EPISeg output
episeg_output=${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-sc_epi
episeg_json=${episeg_output%}.json
echo '{
    "GeneratedBy": [
        {
            "Author": "sct_deepseg -task seg_sc_epi",
            "Date": "'"$(date)"'"
        }
    ]
}' > ${episeg_json}

# For running inference using sct_deepseg_sc model on the BIDS data
sct_deepseg_sc -i ${file_bold} -c t2 -o ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-deepseg.nii.gz

# Create JSON file with deepseg output
deepseg_output=${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-deepseg
deepseg_json=${deepseg_output%}.json
echo '{
    "GeneratedBy": [
        {
            "Author": "sct_deepseg_sc",
            "Date": "'"$(date)"'"
        }
    ]
}' > ${deepseg_json}

# For running inference using sct_propseg model on the BIDS data
# Check if the file with _seg-propseg.nii.gz already exists
if [ ! -f ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-propseg.nii.gz ]; then
    # Run sct_propseg command
    sct_propseg -i ${file_bold} -c t2 -o ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-propseg.nii.gz
    # Removing the centerline file
    rm -rf ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_task-*_centerline.nii.gz

    # Create JSON file with propseg output
    propseg_output=${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-propseg
    propseg_json=${propseg_output%}.json
    echo '{
        "GeneratedBy": [
            {
                "Author": "sct_propseg",
                "Date": "'"$(date)"'"
            }
        ]
    }' > ${propseg_json}
fi


sct_qc -i ${file_bold} -s ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-sc_epi.nii.gz -p sct_deepseg_sc -qc ${PATH_QC}
sct_qc -i ${file_bold} -s ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-deepseg.nii.gz -p sct_deepseg_sc -qc ${PATH_QC}
sct_qc -i ${file_bold} -s ${PATH_DATA}/derivatives/labels/${SUBJECT}/func/${SUBJECT}_seg-propseg.nii.gz -p sct_propseg -qc ${PATH_QC}
