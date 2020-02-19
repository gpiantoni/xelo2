from bidso.utils import add_underscore


def convert_events(run, base_name):
    events_tsv = add_underscore(base_name, '_events.tsv')
    events_tsv.touch()
