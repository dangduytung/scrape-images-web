import re
import mimetypes
from datauri import DataURI


def get_mimetype(data: str):
    try:
        uri = DataURI(data)
        return uri.mimetype
    except Exception as e:
        print(f'Error get mimetype: {e}')
        return None


def get_extension(mimetype):
    """
    https://mimetype.io/all-types
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    """
    extension = mimetypes.guess_extension(mimetype)
    if extension is None:
        extension = '.'
        extension += re.sub(r"[/+-.]", "_", mimetype)
    return extension