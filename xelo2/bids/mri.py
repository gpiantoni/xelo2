from shutil import move
from logging import getLogger
from pathlib import Path

from bidso.utils import remove_underscore

from .io.parrec import convert_parrec_nibabel
from .utils import find_next_value

lg = getLogger(__name__)


def convert_mri(run, rec, dest_path, stem):
    """Return base name for this run"""

    file = _select_parrec(rec)
    if file is None:
        return None

    input_nii = convert_parrec_nibabel(file.path)

    output_nii = dest_path / fr'{stem}_run-(\d)_{rec.modality}.nii.gz'
    output_nii = find_next_value(output_nii)

    move(input_nii, output_nii)

    return remove_underscore(output_nii)


def _select_parrec(rec):
    parrec = []
    for file in rec.list_files():
        if file.format == 'parrec':
            parrec.append(file)

    if len(parrec) == 0:
        lg.warning(f'No file for {rec}')
        return None

    elif len(parrec) > 1:
        lg.warning(f'Too many files for {rec}')  # TODO
        return None

    file = parrec[0]
    if not Path(file.path).exists():
        lg.warning(f'{rec} does not exist')
        return None

    return file
