from shutil import move
from logging import getLogger
from pathlib import Path
from json import dump

from nibabel import save as nisave
from nibabel import load as niload
from bidso.utils import replace_extension

from .io.parrec import convert_parrec_nibabel
from .utils import find_next_value, rename_task

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

    _fix_tr(output_nii, run.RepetitionTime)

    sidecar = _convert_sidecar(run, rec)
    sidecar_file = replace_extension(output_nii, '.json')

    with sidecar_file.open('w') as f:
        dump(sidecar, f, indent=2)

    return output_nii


def _fix_tr(nii, RepetitionTime):

    img = niload(str(nii))

    # this seems a bug in nibabel. It stores time in sec, not in msec
    img.header.set_xyzt_units('mm', 'sec')

    if RepetitionTime is not None:
        img.header['pixdim'][4] = RepetitionTime

    nisave(img, str(nii))


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


def _convert_sidecar(run, rec):
    D = {}
    if rec.modality == 'bold':
        D = {
            'RepetitionTime': rec.RepetitionTime,
            'TaskName': rename_task(run.task_name),
            }

    return D
