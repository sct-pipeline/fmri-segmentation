'''
This script converts data from fMRI BIDS format (received from different sites) to ivadomed compatible BIDS format
The fMRI BIDS format looks like the following:

data_{site_name}_{task}
├── derivatives
│   ├── labels
│   │   ├── sub-01
│   │   │   ├── func
│   │   │   │   ├── sub-{number}_{task_name}-spinalcord_mask.nii.gz
│   ├── moco
│   │   ├── sub-01
│   │   │   ├── func
│   │   │   │   ├── sub-{number}_{task_name}-mocomean_bold.nii.gz

The ivadomed compatible BIDS format looks like the following:

data_{site_name}_{task}_BIDS
├── derivatives
│   ├── labels
│   │   ├── sub-{number}
│   │   │   ├── func
│   │   │   │   ├── sub-{number}_{name}_seg-manual.nii.gz
│   │   │   │   ├── sub-{number}_{name}_seg-manual.json

├── sub-01
│   ├── func
│   │   ├── sub-{number}_{name}_bold.nii.gz
│   │   ├── sub-{number}_{name}_bold.json
├── dataset_description.json
├── participants.tsv
├── participants.json
├── README


Usage:
1. Change the input_path, label_path and output_path to the appropriate paths
2. Run the script by typing the following command in the terminal:
python BIDSify_fMRI_data.py

Author: Rohan Banerjee

'''


import os
import shutil
import json
import argparse
import csv

main_path = os.getcwd()

# input path is the path where the motion corrected image files are stored
input_path = "/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_geneva_rest/data_geneva_rest3/derivatives/moco"
# label path is the path where the spinal cord label files/ground truth are stored
label_path = "/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_geneva_rest/data_geneva_rest3/derivatives/label"
# output path is the path where the BIDSified data will be stored
output_path = "/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/data_geneva_rest3_bids"




if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.makedirs(output_path)
i = 0
all_subjects = []

def convert():

    all_files = os.listdir(input_path)

    for file in all_files:

        os.makedirs(output_path + "/" + file)
        os.makedirs(output_path + "/" + file + "/func")
        
        all_nii_file = os.listdir(input_path + "/" + file + "/func")
        data_json_label = {}
        for nii_file in all_nii_file:
            if nii_file.endswith('_desc-mocomean_bold.nii.gz'):
                shutil.copy2(input_path + "/" + file + "/func/" + nii_file, output_path + "/" + file + "/func")
                os.rename(output_path + "/" + file + "/func/" + nii_file, output_path + "/" + file + "/func/" + file + "_task-rest_bold.nii.gz")
                

            with open(output_path + "/" + file + "/func/" + file + "_task-rest_bold.json", 'w') as outfile:
                outfile.write(json.dumps(data_json_label, indent=2, sort_keys=True))
            outfile.close()

        

        dataset_description = {"BIDSVersion": "BIDS 1.6.0",
                           "Name": "unknown", 
                           "PipelineDescription": {
                                            "Name": "unknown"}
                           }

        label_files = os.listdir(label_path + "/" + file + "/func")
        os.makedirs(output_path + "/derivatives/labels/" + file + "/func")
        for label in label_files:
            if label.endswith('task-rest_desc-spinalcord_mask.nii.gz'):
                
                shutil.copy2(label_path + "/" + file + "/func/" + label, output_path + "/derivatives/labels/" + file + "/func")
                os.rename(output_path + "/derivatives/labels/" + file + "/func/" + file + "_task-rest_desc-spinalcord_mask.nii.gz", output_path + "/derivatives/labels/" + file + "/func/" + file + "_task-rest_bold_seg-manual.nii.gz")
                data_json_label = {}
                data_json_label[u'Author'] = ""
                data_json_label[u'Label'] = "Manual segmentation over leipzig samples"
                with open(output_path + "/derivatives/labels/" + file + "/func/" + file + "_task-rest_bold_seg-manual.json", 'w') as outfile:
                    outfile.write(json.dumps(data_json_label, indent=2, sort_keys=True))
                outfile.close()


    with open(output_path + '/derivatives/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description, json_file, indent=4)

    with open(output_path + '/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description, json_file, indent=4)

    # Create README
    with open(output_path + '/README', 'w') as readme_file:
        readme_file.write('BIDSify stanford data')


    participants = []
    for subject in all_files:
        row_sub = []
        row_sub.append(subject)
        row_sub.append('n/a')
        row_sub.append('n/a')
        participants.append(row_sub)

    print(participants)
    with open(output_path + '/participants.tsv', 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(["participant_id", "sex", "age"])
        for item in participants:
            tsv_writer.writerow(item)

    # Create participants.json
    #TODO : take the dataset decription from the dataset provided by the site
    data_json = {"participant_id": {
        "Description": "Unique Participant ID",
        "LongName": "Participant ID"
        },
        "sex": {
            "Description": "M or F",
            "LongName": "Participant sex"
        },
        "age": {
            "Description": "yy",
            "LongName": "Participant age"}
    }

    with open(output_path + '/participants.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)


convert()