# fmri-segmentation
Repository for the project on automatic spinal cord segmentation based on fMRI EPI data

<details open>
<summary>To share data for the project, please expand this text!</summary>
<br>

## Aim
To develop a method to automate the time-consuming segmentation
of the spinal cord for fMRI and then make the method openly available to the spinal cord fMRI community. The model will be incorporated into the [Spinal Cord Toolbox](https://spinalcordtoolbox.com/). The data will be used only for the purpose of segmenting the spinal cord. Co-authorship on any abstracts or publications will be offered to anyone who contributes data to the project.

## What to share?
GitHub repository that contains the example data: https://github.com/sct-pipeline/fmri-segmentation/tree/main/data_leipzig_rest

To facilitate the collection, sharing and processing of data, we use the [BIDS standard](https://bids.neuroimaging.io/). An example of the data structure for one center is shown below:
```
data_leipzig_rest
   ├── dataset_description.json
   ├── derivatives
   │   ├── label
   │   │   └── sub-leipzigR01
   │   │       └── func
   │   │           └── sub-leipzigR01_task-rest_desc-spinalcord_mask.nii.gz  <---- Manual spinal cord segmentation
   │   └── moco
   │       └── sub-leipzigR01
   │           └── func
                   ├── sub-leipzigR01_task-rest_desc-moco_bold.json       <---- sidecar json file containing imaging parameters
   │               ├── sub-leipzigR01_task-rest_desc-moco_bold.nii.gz     <---- 20 motion-corrected EPI volumes                 
   │               └── sub-leipzigR01_task-rest_desc-mocomean_bold.nii.gz <---- Mean of motion-corrected volumes
   ├── participants.json
   ├── participants.tsv
   └── task-rest_bold.json
   ```
[dcm2niix](https://github.com/rordenlab/dcm2niix) can be used to convert DICOM files to NiftI (*.nii.gz*) format.

### A. Site Information
**dataset_description.json** ---> Change according to your dataset
```
{
	"Name":   "data_leipzig_rest",
	"Dataset Description": "This is a data set consisting of resting-state spinal cord fMRI data from 1 healthy participant.",
	"DatasetType": "derivative",
	"Generated by":
	[
    {
      "Name": "motion correction",
      "Description": "A two-step motion correction procedure (with spline interpolation) was applied to the EPI time-series data. Initially, the mean of all volumes (250 volumes) was calculated in order to serve as the target image for the first step of motion correction. Based on this mean image, the spinal cord was automatically segmented in order to provide a spinal cord centerline that then served as input for creating a cylindrical mask (with a diameter of 30 mm). This mask was employed during the motion-correction procedure in order to ensure that regions moving independently from the cord would not adversely affect motion estimation. Slice-wise motion correction with a second degree polynomial regularization in the z-direction was then performed. In the second step, a new target image was obtained by calculating the mean of motion-corrected images from the first step and the raw images were realigned to this new target image, using the identical procedure as described above.",
      "Software and version": "Spinal cord toolbox, v 4.2.2"
        },
    {
      "Name": "Segmentation",
      "Description  (Automated, Semi-automated, Manual)": "semi- automated segmentation of the spinal cord",
      "Author (First Name, Last Name)": "Merve Kaptan",
      "Software and version": "Spinal Cord Toolbox, v 4.2.2"
    }
  ],

	"Institution": "Max Planck Institute for Human Cognitive and Brain Sciences, Leipzig, Germany",
	"Co-authors (LastName, FirstName ; LastName, FirstName ...)": "Kaptan, Merve; Finsterbusch, Juergen; Eippert, Falk",
	"Contact person (FirstName LastName email)": "Merve Kaptan mkaptan@stanford.edu",
	"Reference": "Kaptan, M., Vannesjo, S. J., Mildner, T., Horn, U., Hartley-Davies, R., Oliva, V., Brooks, J., Weiskopf, N., Finsterbusch, J., & Eippert, F. (2022). Automated slice-specific z-shimming for functional magnetic resonance imaging of the human spinal cord. Human brain mapping, 10.1002/hbm.26018. https://doi.org/10.1002/hbm.26018.",
	"Funding info": "European Research Council under the European Union’s Horizon 2020 research and innovation programme (grant agreement No 758974)."
}
```


### B. Participant information
**participants.json** (this file is generic, you don’t need to change anything there. Just create a new file with this content)
```
{
    "age": {
        "Description": "Age of the participant",
        "Units": "years"
    },
    "sex": {
        "Description": "Sex of the participant",
        "Levels": {
            "M": "Male",
            "F": "Female"
        }
    },
}
```
**participants.tsv** (Tab-separated values)
```
participant_id  age sex
sub-leipzigR01  21  F
````
### C. fMRI data
Please share **one run** of each participant within one **session** and do **not** share data from same participants within each study. <br />
Please only share *.nii.gz* files and **not** *.nii* files.

Task information: See the **task-xx_bold.json**. Include a brief description of the functional task.
1. 	20 motion-corrected EPI volumes <br />
Naming: **sub-XX_task-XX_desc-moco_bold.nii.gz**
2. Sidecar .json file containing information about the acquisition (can be obtained using [dcm2niix](https://github.com/rordenlab/dcm2niix))
Naming: **sub-XX_task-XX_desc-moco_bold.json**
3. 	Mean of motion-corrected volumes (please share the mean image that was used to draw the spinal cord mask) <br />
Naming: **sub-XX_task-XX_desc-mocomean_bold.nii.gz**
4. 	Spinal cord masks that were generated based on mean of motion-corrected volumes. Note: Only include the slices that were used in the subject-level analysis. <br />
Naming: **sub-XX_task-XX_desc-spinalcord_mask.nii.gz**

> **Volume**: an individual data acquisition point. <br />
> **Run**: multiple volumes acquired as one continuous stream of data. <br />
> **Session**: a set of multiple runs during which subjects remained inside the bore of the magnet.

#### How to name your participants?
Name the dataset folder like following:
data_**NameoftheSite**_**NameoftheTask** ---> for example: data_leipzig_rest, data_leipzig_pain, data_northwestern_pain, data_stanford_motor

Name the subjects like following: sub-**NameorAcronymfortheSiteSubjectNumber**
>  data_leipzig_rest/
  >> sub-leipzigR01 <br />
  >> sub-leipzigR02 <br />
  ...

If you are sharing multiple datasets from different studies:
- Have a separate folder for each different study such as: data_northwestern_pain, data_northwestern_motor
- Within these folders, give unique names to each participant such as

>  data_northwestern_motor/
  >> sub-nwM01 <br />
  >> sub-nwM02

> data_northwestern_pain/
>> sub-nwP01 <br />
>> sub-nwP02 <br />
>> .... <br />
sub-nwP10


## How to share?
Once you organize your data as described above you could send it to Merve Kaptan (mkaptan@stanford.edu) via any cloud-based method (Gdrive, Dropbox, etc.).

## Contribute

[Project management](https://github.com/orgs/sct-pipeline/projects/1)

## Ethics and anonymization
We intend to make the dataset publicly available on https://openneuro.org/ for replication and reproduction. It is responsibility of each site to ensure that each subject consented to be scanned and to have their anonymized data put in a publicly-available repository.

</details>

#### [Internal] Link to dataset and segmentation model weights: [here](https://drive.google.com/drive/folders/14rxPz_mWV1AOSULBFFU7A5IT9zX5PvcI?usp=sharing)

## Getting started

- [Spinal Cord Toolbox (SCT)](https://spinalcordtoolbox.com/user_section/installation.html)
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) 
- Python
- [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet)

### Step 1: Cloning the Repository

Open a terminal and clone the repository using the following command:

~~~
git clone https://github.com/sct-pipeline/fmri-segmentation.git
cd fmri-segmentation
~~~

### Step 2: Setting up the Environment & Analysis

The following commands show how to set up the environment. 
Note that the documentation assumes that the user has `conda` installed on their system. 
Instructions on installing `conda` can be found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

1. Create a conda environment with the following command:
```
conda create -n fmri_seg python=3.9
```

2. Activate the environment with the following command:
```
conda activate fmri_seg
pip install -r scripts/run_nnunet_inference_requirements.txt
```

3. Install nnUNetv2 from the [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet):
```
pip install nnunetv2
export nnUNet_raw="${HOME}/nnUNet_raw"
export nnUNet_preprocessed="${HOME}/nnUNet_preprocessed"
export nnUNet_results="${HOME}/nnUNet_results"
```


4. Download the dataset from [here](https://drive.google.com/drive/folders/14rxPz_mWV1AOSULBFFU7A5IT9zX5PvcI?usp=sharing) (soon to be open-sourced on Openneuro)

5. Uzip the data and run the following to convert into nnUNetv2 dataset format:
```
cd scripts
python convert_bids_to_nnUNetV2.py --path-data <PATH_TO_DOWNLOADED_BIDS_DATASET> --path-out <PATH_TO_/nnUNet_raw> --split 0.8 0.2 --seed 42 --contrast bold --label-suffix seg-manual --data-type func --dataset-name <DATASET_NAME> --dataset-number <DATASET_ID> --copy True
```

6. To train 3D model (as per nnUNetv2 documentation):
```
nnUNetv2_plan_and_preprocess -d <DATASET_ID> --verify_dataset_integrity
CUDA_VISIBLE_DEVICES=<GPU_ID> nnUNetv2_train <DATASET_ID> 3d_fullres <FOLD_NUMBER>
```
7. For inference:
- [TEMPORARY] Download the cuurent best model weights from [here](https://drive.google.com/drive/folders/1AF2Q_8OQ63mK1biir59QYAiTG4wCHen4?usp=share_link) (will be released as assets later)
```
[NOTE] A BIDS dataset is NOT required for inference. A folder containing the images is good enough to run the inference
python scripts/run_nnunet_inference.py --path-dataset <PATH_TO_DATASET> --path-out <PATH_TO_OUTPUT_FOLDER> --path-model <PARENT_FOLDER_CONTAINING_ALL_FOLDS>

```




