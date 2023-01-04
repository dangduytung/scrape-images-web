import random
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


def ua_random_fallback(ua_default):
    ua = UserAgent(fallback=ua_default)
    return ua.random


def ua_random_from_file(file_ua):
    lines = open(file_ua).read().splitlines()
    ua = random.choice(lines)
    return ua