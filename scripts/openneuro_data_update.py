import os
import shutil
import datetime
import json

# step 1: takes a yml files as the input which contains all the names of the subjects which were manually corrected
# step 2: This copies the segmentation files from the nnUNet dataset and copies it to the derivatives/labels folder in the openneuro dataset
# step 2.1: Rename the files as per the openneuro dataset
# step 3: Update the json files linked to the dataset like the below
# If the segmnetation json file already has
# {
#     "SpatialReference": "orig",
#     "GeneratedBy": [
#         {
#             "Name": "Manual",
#             "Author": "Nawal Kinany"
#         },
#         {
#             "Name": "Manually corrected after initial segmentation done by EPISeg model (https://github.com/sct-pipeline/fmri-segmentation/releases/tag/v0.2)",
#             "Author": "Rohan Banerjee adn Merve Kaptan"
#             "Date": "<date and time from file metadata>" 
#         }
#     ]
# }

def read_subjects_from_yaml(file_path):
    with open(file_path, 'r') as file:
        subjects = file.read().splitlines()
    return subjects

subjects = read_subjects_from_yaml('input.yml')

import argparse

def main():
    parser = argparse.ArgumentParser(description='Update dataset with segmentation files')
    parser.add_argument('-nnunet-dataset', type=str, help='Path to nnUNet dataset')
    parser.add_argument('-openneuro-dataset', type=str, help='Path to openneuro dataset')
    parser.add_argument('-corrected-subjects', type=str, help='Path to input file containing subjects')
    args = parser.parse_args()

    nnunet_dataset = args.nnunet_dataset
    openneuro_dataset = args.openneuro_dataset
    input_file = args.corrected_subjects

    subjects = read_subjects_from_yaml(input_file)

    # Step 2: Copy the segmentation files to the derivatives/labels folder
    for subject in subjects:
        #todo: add a arguement to get the nnUnet dataset prefix, I am currently assuming it to be spinefmri (as per my dataset)
        source_path = f'{nnunet_dataset}/labelsTr/spinefmri_{subject}.nii.gz'
        #logic: remove the already existing segmentation file and copy the manually segmented one in place of it
        destination_path = f'{openneuro_dataset}/derivatives/labels/{subject}_task-*_desc-spinalcordmask.nii.gz'
        task = destination_path.split('_task-')[1].split('_desc')[0]
        if os.path.exists(destination_path):
            os.remove(destination_path)
        shutil.copyfile(source_path, destination_path)
        os.rename(destination_path, f'{openneuro_dataset}/derivatives/labels/{subject}_task-{task}_desc-spinalcordmask.nii.gz')

    # Step 3: Update the JSON files linked to the dataset
    json_file_path = f'{openneuro_dataset}/dataset_description.json'
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    json_data['GeneratedBy'] = [
        {
            'Name': 'Manual',
            'Author': 'Nawal Kinany'
        },
        {
            'Name': 'Manually corrected after initial segmentation done by EPISeg model (https://github.com/sct-pipeline/fmri-segmentation/releases/tag/v0.2)',
            'Author': 'Rohan Banerjee and Merve Kaptan',
            'Date': str(datetime.datetime.now())
        }
    ]
    with open(json_file_path, 'w') as file:
        json.dump(json_data, file, indent=4)

if __name__ == '__main__':
    main()