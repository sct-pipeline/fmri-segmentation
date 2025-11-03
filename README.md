# Automatic Spinal Cord Segmentation on gradient-echo EPI Data
Repository for the project containing training information, model weights and inference instructions. The code is based on the [nnUNetv2 framework](https://github.com/MIC-DKFZ/nnUNet).
Dataset used for this project is open-sourced! Find it [here](https://openneuro.org/datasets/ds005143/versions/1.2.1) on Openneuro.

> [!Important]  
> If you use this model, please cite:
> 
> Banerjee R, Kaptan M, Tinnermann A, Khatibi A, Dabbagh A, Büchel C, Kündig CW, Law CSW, Pfyffer D, Lythgoe DJ, Tsivaka D, Van De Ville D, Eippert F, Muhammad F, Glover GH, David G, Haynes G, Haaker J, Brooks JCW, Finsterbusch J, Martucci KT, Hemmerling KJ, Mobarak-Abadi M, Hoggarth MA, Howard MA, Bright MG, Kinany N, Kowalczyk OS, Freund P, Barry RL, Mackey S, Vahdat S, Schading S, McMahon SB, Parish T, Marchand-Pauvert V, Chen Y, Smith ZA, Weber KA II, De Leener B, Cohen-Adad J. EPISeg: Automated segmentation of the spinal cord on echo planar images using open-access multi-center data. Imaging Neurosci (Camb) [Internet]. 2025 Jul 21 [cited 2025 Sep 2]; Available from: https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.98/131869/EPISeg-Automated-segmentation-of-the-spinal-cord
  


To share data for the project, please read wiki [here](https://github.com/sct-pipeline/fmri-segmentation/wiki/Data-contribution-details)! 

Dataset: https://openneuro.org/datasets/ds005143/versions/1.3.1 

#### Link to latest segmentation model weights: [here](https://github.com/sct-pipeline/fmri-segmentation/releases/tag/v0.2)

## Getting started

- [Spinal Cord Toolbox (>=v7.1)](https://spinalcordtoolbox.com/user_section/installation.html)
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) 
- Python
- [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet)


## To run inference on your data, follow the below steps:
```
usage: sct_deepseg sc_epi [-i <file> [<file> ...]] [-o <str>] [-install]
                          [-custom-url CUSTOM_URL [CUSTOM_URL ...]]
                          [-largest {0,1}] [-fill-holes {0,1}]
                          [-remove-small REMOVE_SMALL [REMOVE_SMALL ...]]
                          [-qc <folder>] [-qc-dataset <str>] [-qc-subject <str>]
                          [-qc-plane <str>] [-qc-seg <file>] [-h] [-v <int>]
                          [-profile-time [<file>]] [-trace-memory [<folder>]]
                          [-r {0,1}]
```
Project url: https://spinalcordtoolbox.com/stable/user_section/command-line/deepseg/sc_epi.html

## To reproduce the model training:

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
pip install -r inference/requirements.txt
```

3. Install nnUNetv2 from the [nnUNetv2](https://github.com/MIC-DKFZ/nnUNet):
```
pip install nnunetv2
export nnUNet_raw="${HOME}/nnUNet_raw"
export nnUNet_preprocessed="${HOME}/nnUNet_preprocessed"
export nnUNet_results="${HOME}/nnUNet_results"
```


4. Download the dataset from [OpenNeuro]([https://openneuro.org/datasets/ds005143](https://openneuro.org/datasets/ds005143/versions/1.2.0))

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



