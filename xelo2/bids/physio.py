import gzip
from json import dump

from bidso.utils import replace_extension, add_underscore, remove_underscore

from .io.dataglove import parse_dataglove_log
from .io.pulse_and_resp_scanner import parse_scanner_physio


def convert_physio(rec, data_name):
    base_name = remove_underscore(data_name)

    for file in rec.list_files():
        if file.format == 'dataglove':
            rec_name = 'dataglove'
            tsv, hdr = parse_dataglove_log(file.path)

        elif file.format == 'scanphyslog':
            rec_name = 'resp'
            tsv, hdr = parse_scanner_physio(file.path)

        else:
            return

        hdr['StartTime'] = rec.onset

    physio_tsv = add_underscore(base_name, f'rec-{rec_name}_physio.tsv.gz')
    _write_physio(tsv, physio_tsv)

    physio_json = replace_extension(physio_tsv, '.json')
    with physio_json.open('w') as f:
        dump(hdr, f, indent=2)


def _write_physio(physio, physio_tsv):

    content = physio.to_csv(sep='\t', index=False, header=False, float_format='%.3f')
    with gzip.open(physio_tsv, 'wb') as f:
        f.write(content.encode())
