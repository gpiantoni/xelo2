from logging import getLogger
from json import dump
from os import environ
from pathlib import Path
from shutil import move, copyfile, copyfileobj
from subprocess import run, DEVNULL
from tempfile import mkstemp, gettempdir
import gzip

from nibabel import save as nisave
from nibabel import load as niload
from bidso.utils import replace_extension

from .io.parrec import convert_parrec_nibabel
from .utils import rename_task, make_bids_name, find_one_file, make_taskdescription

lg = getLogger(__name__)


def convert_mri(run, rec, dest_path, name, deface=True):
    """Return base name for this run"""
    output_nii = dest_path / f'{make_bids_name(name)}_{rec.modality}.nii.gz'

    file = find_one_file(rec, ('parrec', ))
    if file is not None:
        input_nii = convert_parrec_nibabel(file.path)
        move(input_nii, output_nii)

    else:
        file = find_one_file(rec, ('nifti', ))
        if file is None:
            return None

        else:
            input_nii = file.path

            if input_nii.name.endswith('.nii.gz'):
                copyfile(file.path, output_nii)
            elif input_nii.name.endswith('.nii'):
                gz(file.path, output_nii)
            else:
                lg.warning(f'Unknown extension for nifti for {input_nii}')
                return None

    if run.task_name == 'MP2RAGE':
        lg.info('Keeping only the first volume for MP2RAGE')
        select(output_nii, 'first')

    _fix_tr(output_nii, rec.RepetitionTime)

    if deface and rec.modality in ('T1w', 'T2w', 'T2star', 'PD', 'FLAIR'):
        run_deface(output_nii)

    sidecar = _convert_sidecar(run, rec)
    sidecar_file = replace_extension(output_nii, '.json')

    with sidecar_file.open('w') as f:
        dump(sidecar, f, indent=2)

    return output_nii


def select(nii, slicing):
    img = niload(nii)
    if slicing == 'first':
        img = img.slicer[:, :, :, 0]
    img.to_filename(nii)


def _fix_tr(nii, RepetitionTime):

    img = niload(str(nii))

    # this seems a bug in nibabel. It stores time in sec, not in msec
    img.header.set_xyzt_units('mm', 'sec')

    if RepetitionTime is not None:
        img.header['pixdim'][4] = RepetitionTime

    nisave(img, str(nii))


def _convert_sidecar(run, rec):
    D = {
        'InstitutionName': 'University Medical Center Utrecht',
        'InstitutionAddress': 'Heidelberglaan 100, 3584 CX Utrecht, the Netherlands',
        'TaskDescription': make_taskdescription(run),
        }
    if rec.modality == 'bold':
        D = {
            'RepetitionTime': rec.RepetitionTime,
            'TaskName': rename_task(run.task_name),
            }

    return D


def run_deface(nii):
    lg.info(f'Defacing {nii.name}, it might take a while')
    path_avg = Path(environ['FREESURFER_HOME']) / 'average'

    # generate a unique file name in the same folder
    if nii.name.endswith('.nii.gz'):
        suffix = '.nii.gz'
    elif nii.name.endswith('.nii'):
        suffix = '.nii'
    nii_tmp = Path(mkstemp(dir=nii.parent, suffix=suffix)[1])
    nii_tmp.unlink()

    run([
        'mri_deface',  # from freesurfer
        nii,
        path_avg / 'talairach_mixed_with_skull.gca',
        path_avg / 'face.gca',
        nii_tmp],
        stdout=DEVNULL, stderr=DEVNULL,
        cwd=gettempdir(),
        )

    nii_tmp.rename(nii)


def gz(input_file, output_file):
    with input_file.open('rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            copyfileobj(f_in, f_out)
