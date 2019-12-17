from shutil import move

from .io.parrec import convert_parrec_nibabel
from .utils import find_next_value


def convert_func(run, rec, file, dest_path, stem):

    input_nii = convert_parrec_nibabel(file.path)

    output_nii = dest_path / f'{stem}_run-(\d)_{rec.modality}.nii.gz'
    output_nii = find_next_value(output_nii)

    move(input_nii, output_nii)
