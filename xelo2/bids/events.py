from bidso.utils import add_underscore
from ..io.tsv import save_tsv


def convert_events(run, base_name):
    events_tsv = add_underscore(base_name, 'events.tsv')

    save_tsv(events_tsv, run.events)
