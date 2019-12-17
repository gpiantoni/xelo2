from re import search


def find_next_value(path_with_regex):
    r"""Replace (\d) with the next number"""

    max_run = 0
    for p in path_with_regex.parent.iterdir():
        m = search(path_with_regex.stem, p.stem)
        if m is not None:
            max_run = max((max_run, int(m.group(1))))

    return path_with_regex.parent / path_with_regex.name.replace(r'(\d)', str(max_run + 1))
