import os
import shutil
import datetime

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
    parser.add_argument('nnunet_dataset', type=str, help='Path to nnUNet dataset')
    parser.add_argument('updated_dataset', type=str, help='Path to dataset to be updated')
    args = parser.parse_args()

    nnunet_dataset = args.nnunet_dataset
    updated_dataset = args.updated_dataset

    subjects = read_subjects_from_yaml('input.yml')

    # Step 2: Copy the segmentation files to the derivatives/labels folder
    for subject in subjects:
        source_path = f'{nnunet_dataset}/{subject}/segmentation.nii.gz'
        destination_path = f'{updated_dataset}/derivatives/labels/{subject}_seg.nii.gz'
        shutil.copyfile(source_path, destination_path)
        # Step 2.1: Rename the files as per the updated dataset
        os.rename(destination_path, f'{updated_dataset}/derivatives/labels/{subject}.nii.gz')

    # Step 3: Update the JSON files linked to the dataset
    json_file_path = f'{updated_dataset}/dataset_description.json'
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