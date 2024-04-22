## Steps to run inference

To run inference on your own data based on your latest EPI segmentation model, run the following steps:

1. Clone this repository
```
git clone https://github.com/sct-pipeline/fmri-segmentation.git` 
```
2. Enter the cloned repository
```
cd fmri-segmentation/inference
```
3. Create and activate a conda environment for the inference
```
conda create -n inference
conda activate inference
```
4. Install requirements
```
pip install -r requirements.txt
```
5. Download the latest model weights from the GDrive link below:
```
The naming convention for models inside the GDrive folder: model_YYYYMMDD
https://drive.google.com/drive/u/0/folders/1AF2Q_8OQ63mK1biir59QYAiTG4wCHen4

Note: Internal for now, please email banerjee.rohan98@gmail.com for access
```



5. Update the placeholders (paths written inside `<>`) and run the following command:
```
python run_inference.py --path-dataset_bids <PATH_TO_BIDS_DATASET> --path-out <PATH_TO_OUTPUT> --path-model <PATH_TO_MODEL> --use-best-checkpoint -path-qc <PATH_TO_QC>
```

## Expected output
There would be a folder named same as mentioned in `--path-out` which would contain the predicted files with the same name as the subject image files. The QC would be present inside the directory mentioned in `--path-qc`
