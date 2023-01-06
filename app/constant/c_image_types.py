# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types
# https://www.checkfiletype.com
EXT_APNG = ['.apng']
MIMETYPE_APNG = 'image/apng'

EXT_AVIF = ['.avif']
MIMETYPE_AVIF = 'image/avif'

EXT_GIF = ['.gif']
MIMETYPE_GIF = 'image/gif'

EXT_JPEG = ['.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp']
MIMETYPE_JPEG = 'image/jpeg'

EXT_PNG = ['.png']
MIMETYPE_PNG = 'image/png'

EXT_SVG = ['.svg']
MIMETYPE_SVG = 'image/svg+xml'

EXT_WEBP = ['.webp']
MIMETYPE_WEBP = 'image/webp'

EXT_BMP = ['.bmp']
MIMETYPE_BMP = 'image/bmp'

EXT_ICO = ['.ico', '.cur']
MIMETYPE_ICO = 'image/x-icon'

EXT_TIFF = ['.tif', '.tiff']
MIMETYPE_TIFF = 'image/tiff'

# https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/mt846532(v=vs.85)
EXT_HEIF = ['.heic', '.heif']
MIMETYPE_HEIF = ['image/heic', 'image/heif']


def img_extend(*args):
    _ret = []
    for arg in args:
        if type(arg) is str:
            _ret.append(arg)
        elif type(arg) is list:
            _ret.extend(arg)
    # print(_ret)
    return _ret


IMG_EXT = img_extend(EXT_APNG, EXT_AVIF, EXT_GIF, EXT_JPEG, EXT_PNG,
                     EXT_SVG, EXT_WEBP, EXT_BMP, EXT_ICO, EXT_TIFF, EXT_HEIF)
IMG_MIMETYPE = img_extend(MIMETYPE_APNG, MIMETYPE_AVIF, MIMETYPE_GIF, MIMETYPE_JPEG, MIMETYPE_PNG,
                          MIMETYPE_SVG, MIMETYPE_WEBP, MIMETYPE_BMP, MIMETYPE_ICO, MIMETYPE_TIFF, MIMETYPE_HEIF)
