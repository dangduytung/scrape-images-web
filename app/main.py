import os
import sys
import re
import datetime
from time import gmtime, strftime
import random
import requests
from bs4 import BeautifulSoup
import cssutils
import uuid
# import imghdr
from datauri import DataURI
from py_log import log
# from py_log_print import log
import constant.c_user_agents as UserAgents
import constant.c_image_types as ImageTypes
import util.u_urls as UtilUrls
import util.u_files as UtilFiles
import util.u_images as UtilImages


FOLDER_IMAGES = 'data\\images'
FILE_USER_AGENTS = 'assets\\user_agents.txt'

# USER_AGENTS = UserAgents.UA
USER_AGENTS = None

count_success: int = 0
hostname = ''
image_names = []
folder_image = ''  # folder contain images by once download


def clear():
    global count_success
    global hostname
    global image_names
    global folder_image

    count_success = 0
    hostname = ''
    image_names = []
    folder_image = ''


def ua_random():
    global USER_AGENTS

    # Read from file config
    if USER_AGENTS is None:
        log.info(f'read USER_AGENTS from file {FILE_USER_AGENTS} start')
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, FILE_USER_AGENTS)
        USER_AGENTS = open(file_path).read().splitlines()
        log.info(f'read USER_AGENTS len: {len(USER_AGENTS)} end')

    # Read from constant file .py
    if USER_AGENTS is None:
        log.info('read USER_AGENTS from constant')
        USER_AGENTS = UserAgents.UA
        log.info(f'read USER_AGENTS from constant len: {len(USER_AGENTS)} end')

    return random.choice(USER_AGENTS)


def gen_folder_by_web():
    global hostname

    path = hostname.replace('://', '_').replace('.', '_')
    path = FOLDER_IMAGES + '/' + path + '_' + uuid.uuid4().hex
    os.makedirs(path)
    return path


def concatenate_image_link(url):
    # If url is dataURI (https://en.wikipedia.org/wiki/Data_URI_scheme)
    if url.startswith('data:'):
        return url

    # If url is like //product.cdn/image
    if url.startswith('//'):
        return 'http:' + url

    # Full URL or not
    if not url.startswith('http:') and not url.startswith('https:'):
        if url.startswith('/'):
            url = hostname + url
        else:
            url = hostname + '/' + url
        log.info(f'concatenate with hostname -> {url}')
    return url


def extract_image_sources(url, headers):
    log.info(f"request url: {url}")
    log.info(f"request headers: {headers}")
    try:
        # Send GET request
        r = requests.get(url, headers=headers)
        # r.raise_for_status()

        content_type = r.headers['Content-Type']
        log.info(f"Content-Type: {content_type}")
        if 'text/html' not in content_type:
            log.warning(f"Url is not html")
            return None

        # Check if the status_code is 200
        if r.status_code == 200:

            # Parse the HTML content of the webpage
            soup = BeautifulSoup(r.content, 'html.parser')

            image_links = set()

            """
            Find tag `img`
            """
            # Find all of the image tags:
            images = soup.findAll('img')

            # Extract 'src' attribute of every image
            for image in images:
                _url = image.attrs['src']
                image_links.add(concatenate_image_link(_url))

            """
            Find style `background-image`
            """
            arr_div_style = soup.find_all(
                lambda tag: tag.name == "div" and 'style' in tag.attrs)

            for div_style in arr_div_style:
                style = cssutils.parseStyle(div_style['style'])
                _url = style['background-image']
                _url = _url.replace('url(', '').replace(')', '')
                if _url != '':
                    log.info(f'background-image: {_url}')
                    image_links.add(concatenate_image_link(_url))

            return image_links
        else:
            log.warning(f"request url: {url}, response code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"Error: {e}")


def save_image(source):
    """
    Save image by URL, dataURI
    """
    global count_success

    log.info(f"start source: {source}")

    file_name = None

    # Decode or download image
    if source.startswith('data:'):
        file_name = decode_image_data_uri(source)
    else:
        file_name = download_image(source)

    # Count and log
    if file_name is not None:
        count_success += 1
        log.info(f"success save image: {file_name}, count: {count_success}")
    else:
        log.warning(f"can not save image of source: {source}")
    return file_name


def decode_image_data_uri(data):
    """
    Decode image dataURI
    """
    log.info(f"data URI: {data}")

    try:
        uri = DataURI(data)
    except Exception as e:
        log.error(f'Error: {e}')
        return None

    mimetype = uri.mimetype
    extension = UtilImages.get_extension(mimetype)
    file_name = uuid.uuid4().hex + extension
    path = folder_image + '/' + file_name

    # Write file
    if isinstance(uri.data, str):
        UtilFiles.write_text(uri.data, path)
    elif isinstance(uri.data, bytes):
        UtilFiles.write_bytes(uri.data, path)
    else:
        log.warning(f"type(uri.data): {type(uri.data)}")
    return file_name


def download_image(url):
    """
    Download image by URL
    """

    global count_success
    global hostname
    global image_names

    log.info(f"start url: {url}")

    try:
        user_agent = ua_random()
        headers = {'User-Agent': user_agent}

        log.info('headers: ' + str(headers))
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        log.error(f"Error requesting url: {url}, {e}")
        return None

    # log.debug('response content: ' + str(response.content))

    if not response:
        log.warning(f"Unable to verify the signature of the image, url: {url}")
        return None

    """
    http://www.iana.org/assignments/media-types/media-types.xhtml
    """
    # Check Content-Type
    content_type = response.headers['Content-Type']
    log.info(f"response Content-Type: {content_type}")

    if 'image' not in content_type:
        log.warning(f"image not in Content-Type, url: {url}")
        return None

    # Get extension by Content-Type
    temp = re.findall(r"[\w']+", content_type)
    extension = temp[1]

    """
    https://docs.python.org/3/library/imghdr.html
    """
    # # Check content response is image type
    # image_type = imghdr.what('', response.content)
    # log.info(f"image_type: {image_type}, url: {url}")
    # if not image_type:
    #     log.info("Image type not detected in response")
    #     return None
    # log.info(f"Image type detected: {image_type}")

    """
    Get file name
    """
    file_name = None
    # Get file name by content-disposition
    if 'content-disposition' in response.headers:
        content_disposition = response.headers['content-disposition']
        file_names = re.findall("filename=\"(.+)\"", content_disposition)
        log.info('file_names:' + str(file_names))
        if file_names:
            file_name = file_names[0]

    """
    Get file name by url like: https://abc.com/img/xyz.png?param=value
    """
    if file_name is None:
        log.info(f'Get file_name from {url}')
        url_without_prams = url.split("?")[0]
        url_last_str = url_without_prams[-5:]
        if len(url_last_str.split(".")) > 1:
            file_ext = '.' + url_last_str.split(".")[1]
            file_ext = file_ext.lower()
            if file_ext in ImageTypes.IMG_EXT:
                file_name = os.path.basename(url_without_prams)

    """
    Get file name by url + extension like: https://abc.com/img/xyz?param=value
    """
    if file_name is None:
        url_without_prams = url.split("?")[0]
        file_name = os.path.basename(url_without_prams)
        # file_name = file_name + '.' + image_type
        file_name += '.' + extension
        log.info(f'file_name: {file_name} from base url: {url}')

    # Generate file name by current time
    if file_name is None:
        extension = os.path.basename(response.headers['Content-Type'])
        extension = extension.split(';')[0]
        file_name = 'image_{0}{1}'.format(
            strftime("%Y%m%d_%H_%M_%S", gmtime()), '.' + str(extension))

    # Check exist image name
    if file_name in image_names:
        file_name = UtilFiles.check_file_name(file_name, image_names)
        log.warning(f'generate new file name {file_name} of {url}')
    image_names.append(file_name)

    # Save image
    UtilFiles.write_bytes(response.content, folder_image + '/' + file_name)

    log.info(f"end file_name: {file_name}")

    return file_name


def scrape_images_web(url):
    global count_success
    global hostname
    global folder_image

    # Clear global variables before start
    clear()

    # Start
    log.info(f"Start scrape images url: {url}")
    time_start = datetime.datetime.now()

    # Check url
    log.info(f"Input url: {url}")
    url = UtilUrls.concatenate_url(url)
    log.info(f"After check url: {url}")

    # Get hostname full
    hostname = UtilUrls.get_hostname_full(url)
    log.info(f"hostname: {hostname}")

    # Define HTTP Headers
    user_agent = ua_random()
    headers = {'User-Agent': user_agent}

    # Extract image links
    image_sources = extract_image_sources(url, headers)
    if not image_sources:
        log.warning(f"No images at url: {url}")
        exit(1)
    log.info("image_sources: " + str(len(image_sources)) + " ~ " + str(image_sources))

    # Generate folder save images
    folder_image = gen_folder_by_web()
    log.info(f"generate folder: {folder_image}")

    # Save all urls (scrape root link and image links)
    _data = url
    for image_source in image_sources:
        _data += '\n' + image_source
    UtilFiles.write_text(_data, folder_image + '/url.txt')

    # Save images (include dataURI, URL)
    [save_image(source) for source in image_sources]

    # End
    time_end = datetime.datetime.now()
    log.info(
        f"Success save images: {count_success} ~ time: " + str(time_end - time_start))
    log.info(f"End scrape images url: {url}")
    log.info('<<<====================================================>>>')


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "Error: No arguments supplied. Please give the url as arguments\nRun the script as:\npy app/main.py [url]")
        exit(1)

    url = sys.argv[1]
    scrape_images_web(url)
