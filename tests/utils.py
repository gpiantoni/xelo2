from os import urandom
from numpy import prod, sum
from nibabel.parrec import parse_PAR_header


def create_random_rec(par_file):
    hdr, image = parse_PAR_header(par_file.open())
    n_bytes = sum(prod(image['recon resolution'], axis=1) * image['image pixel size'] / 8)

    with par_file.with_suffix('.REC').open('wb') as f:
        f.write(urandom(int(n_bytes)))
