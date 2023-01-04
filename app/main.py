import os
import sys
import re
import datetime
from time import gmtime, strftime
import random
import requests
from bs4 import BeautifulSoup
import uuid
# import imghdr
from py_log import log
# from py_log_print import log
import constant.c_user_agents as UserAgents
import constant.c_image_types as ImageTypes
import util.u_urls as UtilUrls


FOLDER_IMAGES = 'data\\images'
FILE_USER_AGENTS = 'assets\\user_agents.txt'

# USER_AGENTS = UserAgents.UA
USER_AGENTS = None

count_success: int = 0
urls_processed = []
hostname = ''


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


def extract_image_links(url, headers):
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

            # Find all of the image tags:
            images = soup.findAll('img')

            # Extract 'src' attribute of every image
            image_links = []
            for image in images:
                image_links.append(image.attrs['src'])
            return image_links
        else:
            log.warning(f"request url: {url}, response code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"Error: {e}")


def download_image(url, folder):
    log.info(f"start url: {url}")

    global count_success
    global urls_processed
    global hostname

    """
    Check processed url
    """
    if (url in urls_processed):
        log.warning(f"url: {url} has processed")
        return None
    urls_processed.append(url)

    # Validate url image
    if not url.startswith('http:') and not url.startswith('https:'):
        url = hostname + url
        log.warning(f'concatenate with hostname -> {url}')

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

    # Save image
    with open(folder + '/' + file_name, 'wb+') as wobj:
        wobj.write(response.content)
    count_success += 1
    log.info(f"success save image: {file_name}, count: {count_success}")

    return file_name


def scrape_images_web(url):
    global count_success
    global hostname

    # Start
    log.info(f"Start scrape images url: {url}")
    time_start = datetime.datetime.now()

    # # Validate input url
    # if not is_url(url):
    #     log.error(f"input: {url} is not URL")
    #     exit(1)

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
    image_links = extract_image_links(url, headers)
    if not image_links:
        log.warning(f"No images at url: {url}")
        exit(1)
    log.info("image_links: " + str(len(image_links)) + " ~ " + str(image_links))

    # Generate folder save images
    folder = gen_folder_by_web()
    log.info(f"generate folder: {folder}")

    # Save url scrape
    with open(folder + '/url.txt', 'w') as wobj:
        wobj.write(url)

    # Download image by links
    count_success = 0
    [download_image(url, folder) for url in image_links]
    log.info(f"Success save images: {count_success}")

    # End
    time_end = datetime.datetime.now()
    log.info(
        f"End scrape images url: {url} ~ time: " + str(time_end - time_start))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "Error: No arguments supplied. Please give the url as arguments\nRun the script as:\npy app/main.py [url]")
        exit(1)

    url = sys.argv[1]
    scrape_images_web(url)
