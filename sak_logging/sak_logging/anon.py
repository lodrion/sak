"""Anonymize stuff for logging"""
from urllib.parse import urlsplit, urlunsplit


def anonymize_url(url: str, remove_username: bool = False) -> str:
    """Anonymize url, optionally removing the username as well as password"""
    parse = urlsplit(url)
    if remove_username and parse.username is not None:
        username = '***'
    else:
        username = parse.username
    if parse.password is not None:
        password = '***'
    else:
        password = None
    host = parse.hostname
    if parse.port:
        host += ':' + parse.port

    if username or password:
        netloc = '{}:{}@{}'.format(username, password, host)
        anonymized = parse._replace(netloc=netloc)
    else:
        anonymized = parse
    return urlunsplit(anonymized)
