import numpy as np
import nibabel as nib
import SimpleITK as sitk

def convert_npy_to_nii(npy_file_path, nii_file_path):
    # Load the .npy file
    data = np.load(npy_file_path)
    # Check if the file is in .npy or .npz format
    if npy_file_path.endswith('.npy'):
        # Load the .npy file
        data = np.load(npy_file_path)
    elif npy_file_path.endswith('.npz'):
        # Load the .npz file
        npz_data = np.load(npy_file_path)
        # Extract the array from the .npz file
        data = npz_data[npz_data.files[]]
    else:
        raise ValueError("Unsupported file format. Only .npy and .npz files are supported.")

    # Create a Nifti1Image object
    img = nib.Nifti1Image(data, np.eye(4))

    # Save the .nii file
    nib.save(img, nii_file_path)

# Usage
convert_npy_to_nii('/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/nnUNet_preprocessed/Dataset021_spinefmri/nnUNetPlans_3d_fullres/spinefmri_sub-kclR06_task-rest_bold.npz', '/home/GRAMES.POLYMTL.CA/robana/duke/temp/rohan/fmri_sc_seg/spinefmri-sub-kclR06_default.nii')