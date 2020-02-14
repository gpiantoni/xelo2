from pathlib import Path


def parse_filetype(file_path):

    data_file = Path(file_path)
    suffix = data_file.suffix.lower()

    if suffix == '.par':
        data_type = 'parrec'

    elif suffix == '.nii' or data_file.name.endswith('.nii.gz'):
        data_type = 'nifti'

    elif suffix == '.img':
        data_type = 'nifti'

    elif suffix == '.dat':
        data_type = 'bci2000'

    elif suffix == '.trc':
        data_type = 'micromed'

    elif suffix == '.nev':
        data_type = 'blackrock'

    elif suffix == '.ns3':
        data_type = 'blackrock'

    elif suffix == '.pdf':
        data_type = 'pdf'

    elif suffix in ('.doc', '.docx'):
        data_type = 'docx'

    elif suffix == '':
        data_type = 'dicom'

    else:
        raise ValueError(f'Unknown file suffix "{suffix}"')

    return data_type
