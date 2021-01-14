def _protocol_name(protocol):
    if protocol.metc == 'Request from clinic':
        return 'Request from clinic'
    elif protocol.date_of_signature is None:
        date_str = 'unknown date'
    else:
        date_str = f'{protocol.date_of_signature:%d %b %Y}'
    return f'{protocol.metc} ({date_str})'


def _name(name):
    if name is None:
        return '(untitled)'
    else:
        return name

def _session_name(sess):
    extra = ''
    if sess.name == 'MRI':
        extra = f'{sess.MagneticFieldStrength} '

    if sess.start_time is None:
        date_str = 'unknown date'
    else:
        date_str = f'{sess.start_time:%d %b %Y}'
    return f'{extra}{sess.name} ({date_str})'
