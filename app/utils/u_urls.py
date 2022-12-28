from urllib.parse import urlparse
from fake_useragent import UserAgent


def is_url(url):
    """
    https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def concatenate_url(url):
    if not url.startswith('http:') and not url.startswith('https:'):
        if url.startswith('www'):
            url = 'http://' + url
        else:
            url = 'http://www.' + url
    return url


def get_hostname_full(url):
    result = urlparse(url)
    return result.scheme + '://' + result.hostname


def ua_random():
    ua = UserAgent()
    return ua.random
