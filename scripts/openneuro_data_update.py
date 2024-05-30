import os
import shutil
import time
import json
import yaml
import argparse
import re
import glob
"""
Usage: python openneuro_data_update.py -nnunet-dataset <PATH_TO_nnUNet> -openneuro-dataset <PATH_TO_OPENNEURO-DATASET> -corrected-subjects <PATH_TO_MANUALLY_CORRECTED_yml_FILE>

Author: Rohan Banerjee
"""

def read_subjects_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    subjects = []
    for path in data["FILES_SEG"]:
        match = re.search(r'sub-[a-zA-Z0-9]+', path)

        if match:
            subject = match.group(0)
            subjects.append(subject)

    return subjects

def main():
    parser = argparse.ArgumentParser(description='Update dataset with segmentation files')
    parser.add_argument('-nnunet-dataset', type=str, help='Path to nnUNet dataset')
    #todo: Download the openneuro dataset from the link to local and update it using the script
    parser.add_argument('-openneuro-dataset', type=str, help='Path to openneuro dataset')
    parser.add_argument('-corrected-subjects', type=str, help='Path to input file containing subjects')
    args = parser.parse_args()

    nnunet_dataset = args.nnunet_dataset
    openneuro_dataset = args.openneuro_dataset
    input_file = args.corrected_subjects

    subjects = read_subjects_from_yaml(input_file)
    existing_subjects = [os.path.splitext(os.path.basename(file))[0].split('_task-')[0] for file in os.listdir(f'{openneuro_dataset}/derivatives/label')]
    subjects = list(set(existing_subjects) & set(subjects))
    print(subjects)

    for i, subject in enumerate(subjects):
        print(subjects[i])
        #todo: add a arguement to get the nnUnet dataset prefix, I am currently assuming it to be spinefmri (as per my dataset)
        files_source = glob.glob(f'{nnunet_dataset}/labelsTr/spinefmri*{subjects[i]}_*.nii.gz')
        if files_source:
            source_path = files_source[0]
        else:
            print(f"No source files found for subject {subjects[i]}")
        #logic: remove the already existing segmentation file and copy the manually segmented one in place of it
        files_destination = glob.glob(f'{openneuro_dataset}/derivatives/label/{subjects[i]}/func/{subjects[i]}_task-*.nii.gz')
        if files_destination:
            destination_path = files_destination[0]
        else:
            print(f"No destination files found for subject {subjects[i]}")
        task = destination_path.split('_task-')[1].split('_desc')[0]
        print(f"Updating {subjects[i]} with the manually corrected segmentation file")
        shutil.copyfile(source_path, destination_path)
        os.rename(destination_path, f'{openneuro_dataset}/derivatives/label/{subjects[i]}/func/{subjects[i]}_task-{task}_desc-spinalcordmask.nii.gz')

        files_destination_json = glob.glob(f'{openneuro_dataset}/derivatives/label/{subjects[i]}/func/{subjects[i]}_task-*.json')
        if files_destination:
            json_file_path = files_destination_json[0]
        else:
            print(f"No destination json files found for subject {subjects[i]}")

        with open(json_file_path, 'r') as outfile:
            json_data = json.load(outfile)

        # Assuming that the metadata already has the 'GeneratedBy' key
        json_data['GeneratedBy'].append({'Name': 'Manual',
                                        'Author': 'Rohan Banerjee and Merve Kaptan (Manually corrected after initial segmentation done by EPISeg model (https://github.com/sct-pipeline/fmri-segmentation/releases/tag/v0.2))',
                                        'Date': time.strftime('%Y-%m-%d %H:%M:%S')})

        with open(json_file_path, 'w') as file:
            json.dump(json_data, file, indent=4)
        print("JSON sidecar for {} was updated".format(subjects[i]))

if __name__ == '__main__':
    main()