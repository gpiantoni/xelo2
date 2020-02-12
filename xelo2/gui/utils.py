LEVELS = (
    'subjects',
    'sessions',
    'protocols',
    'runs',
    'recordings',
    )


def _protocol_name(protocol):
    if protocol.METC == 'Request from clinic':
        return 'Request from clinic'
    elif protocol.date_of_signature is None:
        date_str = 'unknown date'
    else:
        date_str = f'{protocol.date_of_signature:%d %b %Y}'
    return f'{protocol.METC} ({date_str})'
