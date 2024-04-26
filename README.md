# fmri-segmentation
Repository for the project on automatic spinal cord segmentation based on fMRI EPI data

To share data for the project, please read wiki [here](https://github.com/sct-pipeline/fmri-segmentation/wiki/Data-contribution-details)!

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
7. To use this model for your data,
```
Step 1: Install latest SCT version (cd into spinalcordtoolbox and git pull master)
Step 2: sct_deepseg -install-task seg_sc_epi
Step 3: sct_deepseg -task seg_sc_epi -i <IMAGE_PATH> -c bold -o <OUTPUT_PATH>
```




