"""
Run inference on a whole dataset using nnUNetv2 on fMRI BIDS datasets.

Usage: python run_inference.py --path-dataset_bids <PATH_TO_BIDS_DATASET> --path-out <PATH_TO_OUTPUT> --path-model <PATH_TO_MODEL> --use-best-checkpoint -path-qc <PATH_TO_QC>

Authors: Rohan Banerjee 
Initial script author: Naga Karthik
"""

import os
import argparse
import torch
from pathlib import Path
from batchgenerators.utilities.file_and_folder_operations import join
import time
import shutil
import subprocess

# from nnunetv2.inference.predict_from_raw_data import predict_from_raw_data as predictor
# silence nnUNet
if 'nnUNet_raw' not in os.environ:
        os.environ['nnUNet_raw'] = 'UNDEFINED'
if 'nnUNet_results' not in os.environ:
        os.environ['nnUNet_results'] = 'UNDEFINED'
if 'nnUNet_preprocessed' not in os.environ:
        os.environ['nnUNet_preprocessed'] = 'UNDEFINED'
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor


"""
Usage example:
Method 1 (when running on whole dataset):
    python run_inference.py --path-dataset /path/to/test-dataset --path-out /path/to/output --path-model /path/to/model
"""

def get_parser():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Segment images using nnUNet')
    parser.add_argument('--path-dataset_bids', default=None, type=str,
                        help='Path to the test bids dataset folder. Use this argument only if you want '
                        'predict on a whole dataset.')
    parser.add_argument('--path-images', default=None, nargs='+', type=str,
                        help='List of images to segment. Use this argument only if you want '
                        'predict on a single image or list of invidiual images.')
    parser.add_argument('--path-out', help='Path to output directory.', required=True)
    parser.add_argument('--path-qc', help='Path to output directory.', required=True)
    parser.add_argument('--path-model', required=True, 
                        help='Path to the model directory. This folder should contain individual folders '
                        'like fold_0, fold_1, etc.',)
    parser.add_argument('--use-gpu', action='store_true', default=False,
                        help='Use GPU for inference. Default: False')
    parser.add_argument('--use-mirroring', action='store_true', default=False,
                        help='Use mirroring (test-time) augmentation for prediction. '
                        'NOTE: Inference takes a long time when this is enabled. Default: False')
    parser.add_argument('--use-best-checkpoint', action='store_true', default=False,
                        help='Use the best checkpoint (instead of the final checkpoint) for prediction. '
                        'NOTE: nnUNet by default uses the final checkpoint. Default: False')

    return parser


def splitext(fname):
        """
        Split a fname (folder/file + ext) into a folder/file and extension.

        Note: for .nii.gz the extension is understandably .nii.gz, not .gz
        (``os.path.splitext()`` would want to do the latter, hence the special case).
        Taken (shamelessly) from: https://github.com/spinalcordtoolbox/manual-correction/blob/main/utils.py
        """
        dir, filename = os.path.split(fname)
        for special_ext in ['.nii.gz', '.tar.gz']:
            if filename.endswith(special_ext):
                stem, ext = filename[:-len(special_ext)], special_ext
                return os.path.join(dir, stem), ext
        # If no special case, behaves like the regular splitext
        stem, ext = os.path.splitext(filename)
        return os.path.join(dir, stem), ext


def add_suffix(fname, suffix):
    """
    Add suffix between end of file name and extension. Taken (shamelessly) from:
    https://github.com/spinalcordtoolbox/manual-correction/blob/main/utils.py
      
    :param fname: absolute or relative file name. Example: t2.nii.gz
    :param suffix: suffix. Example: _mean
    :return: file name with suffix. Example: t2_mean.nii

    Examples:

    - add_suffix(t2.nii, _mean) -> t2_mean.nii
    - add_suffix(t2.nii.gz, a) -> t2a.nii.gz
    """
    stem, ext = splitext(fname)
    return os.path.join(stem + suffix + ext)

def convert_bids_to_a_folder(path_dataset_bids):

    path_tmp = os.path.join(os.path.dirname(path_dataset_bids), 'tmp')
    if not os.path.exists(path_tmp):
        os.makedirs(path_tmp, exist_ok=True)

    path_tmp_bids = os.path.join(os.path.dirname(path_dataset_bids), 'tmp_bids')
    if not os.path.exists(path_tmp_bids):
        os.makedirs(path_tmp_bids, exist_ok=True)


    for root, dirs, files in os.walk(path_dataset_bids):
        for filename in files:
            if 'bold' in filename and filename.endswith('.nii.gz') and 'seg' not in filename:
                shutil.copy2(root + "/" + filename, path_tmp_bids + "/" + filename)

    for f in os.listdir(path_tmp_bids):
        if f.endswith('.nii.gz') or f.endswith('.png'):
            # get absolute path to the image
            f = os.path.join(path_tmp_bids, f)
            # add suffix
            f_new = add_suffix(f, '_0000')
            # copy to tmp folder
            os.system('cp {} {}'.format(f, os.path.join(path_tmp, os.path.basename(f_new))))


    return path_tmp, path_tmp_bids

def run_qc(path_in, path_out, path_qc):
    for root, dirs, files in os.walk(path_out):
        for filename in files:
            if 'bold' in filename and 'seg' not in filename and filename.endswith('.nii.gz'):
                filename_seg = add_suffix(filename, '_seg-manual')
                sub_name = filename.split("_")[0]
                print(filename, filename_seg)
                root_img, dirs_img = os.path.split(path_in)
                subprocess.run(f"sct_qc -i {root_img}/{dirs_img}/{sub_name}/func/{filename} -s {path_out}/{filename} -qc {path_qc}/qc -p sct_deepseg_sc", shell=True, check=True)
                

def main():

    parser = get_parser()
    args = parser.parse_args()

    if not os.path.exists(args.path_out):
        os.makedirs(args.path_out, exist_ok=True)

    if args.path_dataset_bids is not None and args.path_images is not None:
        raise ValueError('You can only specify either --path-dataset or --path-images (not both). See --help for more info.')
    
    if args.path_dataset_bids is not None:
        print('Found a dataset folder. Running inference on the whole dataset...')

        # NOTE: nnUNet only wants the _0000 suffix for files contained in a folder (i.e. when inference is run on a whole dataset)
        # hence, we create a temporary folder with the proper filenames and delete it after inference is done
        # More info about that naming convention here: 
        # https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md
        
        print('Creating temporary folder with proper filenames...')
        path_data_tmp, path_tmp_bids = convert_bids_to_a_folder(args.path_dataset_bids)
        path_out = args.path_out
        os.system('rm -rf {}'.format(path_tmp_bids))

    elif args.path_images is not None:
        # NOTE: for individual images, the _0000 suffix is not needed. 
        # BUT, the input images should be in a nested list, and the output paths in a list.
        # get list of images from input argument
        print(f'Found {len(args.path_images)} images. Running inference on them...')
        # path_data_tmp = [[os.path.basename(f)] for f in args.path_images]
        path_data_tmp = [[f] for f in args.path_images]
        print(path_data_tmp)

        # path_out = args.path_out
        path_out = []
        # # add suffix '_pred' to predicted images
        for f in args.path_images:
            fname = Path(f).name
            # strip ALL suffixes
            print(fname)
            fname = fname.split(".nii.gz")[0]
            path_pred = os.path.join(args.path_out, add_suffix(fname, '_pred')) 
            path_out.append(path_pred)
        print(path_out)

    # uses all the folds available in the model folder by default
    folds_avail = [f.split('_')[-1] for f in os.listdir(args.path_model) if f.startswith('fold_all')]

    print('Starting inference...')
    start = time.time()
    # instantiate the nnUNetPredictor
    predictor = nnUNetPredictor(
        tile_step_size=0.2,
        use_gaussian=True,
        use_mirroring=True,
        perform_everything_on_gpu=True if args.use_gpu else False,
        device=torch.device('cuda') if args.use_gpu else torch.device('cpu'),
        verbose=False,
        verbose_preprocessing=False,
        allow_tqdm=True
    )
    print('Running inference on device: {}'.format(predictor.device))

    # initializes the network architecture, loads the checkpoint
    predictor.initialize_from_trained_model_folder(
        join(args.path_model),
        use_folds=folds_avail,
        checkpoint_name='checkpoint_final.pth' if not args.use_best_checkpoint else 'checkpoint_best.pth',
    )
    print('Model loaded successfully. Fetching test data...')

    predictor.predict_from_files(
        path_data_tmp, 
        path_out,
        save_probabilities=False, 
        overwrite=False,
        num_processes_preprocessing=2, 
        num_processes_segmentation_export=2,
        folder_with_segs_from_prev_stage=None, 
        num_parts=1, 
        part_id=0
    )
    end = time.time()
    print('Inference done.')


    print('----------------------------------------------------')
    print('Results can be found in: {}'.format(args.path_out))
    print('----------------------------------------------------')

    print('Total time elapsed: {:.2f} seconds'.format(end - start))

    if args.path_qc is not None:
        if args.path_dataset_bids is not None:
            run_qc(args.path_dataset_bids, args.path_out, args.path_qc)
        
        if args.path_images is not None:
            path_images = ''.join(args.path_images)
            # path_images = path_images.split("sub")[0]
            run_qc(path_images, args.path_out, args.path_qc)
    
    print('Deleting the temporary folder...')
    # delete the temporary folder
    os.system('rm -rf {}'.format(path_data_tmp))

if __name__ == '__main__':
    main()