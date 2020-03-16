from logging import getLogger
from pathlib import Path
from nibabel.cmdline.parrec2nii import get_opt_parser, proc_file, verbose
from tempfile import mkdtemp

lg = getLogger(__name__)


def convert_parrec_nibabel(par_file):
    """

    """
    input_par = Path(par_file).resolve()
    tmp_dir = mkdtemp()
    lg.debug(f'Temporary directory for PAR/REC conversion: {tmp_dir}')

    parser = get_opt_parser()
    (opts, infiles) = parser.parse_args([
        '--output-dir=' + tmp_dir,
        '--compressed',
        '--permit-truncated',
        '--store-header',
        '--strict-sort',  # necessary for magnitute / phase
        ] + [str(input_par), ]
        )
    verbose.switch = opts.verbose

    proc_file(infiles[0], opts)

    output = next(Path(tmp_dir).glob('*.nii.gz'))

    return output
