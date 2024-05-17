This folder contains the scripts to run inference on a BIDS dataset using the `sct_deepseg -task seg_sc_epi` which is the latest spinal cord segmentation model for EPI data. 

## Run comparison with other methods:

&#9888; It is expected that you have latest version of SCT installed

This script will run inference on your BIDS dataset using `sct_deepseg_sc`, `sct_propseg`, `sct_deepseg -task seg_sc_contrast-agnostic` and `sct_deepseg -task seg_sc_epi`

Follow the steps below:

1. Enter the directory containing the scripts
```
cd fmri-segmentation/baselines
```

2. Update the paths in the `config,json` file
```
{
    "path_data"   : "PATH_TO_DATASET",
    "path_output" : "PATH_TO_OUTPUT",
    "script"      : "<PATH_TO>/run_seg_methods.sh",
    "jobs"        : -1
}
```

3. Run the `sct_run_batch` command
```
sct_run_batch -config config.json
```

#### Expected outcome: 
You will be able to locate all the segmentation file inside the `derivatives/labels` fodler in your dataset. All the segmentation file from each method can be found inside the respective subject folder.

[UPDATE FOR `get_metrics.py` is still in progress, will be updated soon]
