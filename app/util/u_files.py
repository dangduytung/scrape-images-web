import os


def write_text(data: str, path: str):
    with open(path, 'w+') as file:
        file.write(data)


def write_bytes(data: bytes, path: str):
    with open(path, 'wb+') as file:
        file.write(data)


def check_file_name(file_name_full, arr):
    """
    Check if exist file name in array, so generate new file name ex: a.png -> a(1).png
    """
    idx = 0
    file_name, file_extension = os.path.splitext(file_name_full)
    while file_name_full in arr:
        idx += 1
        file_name_full = file_name + '(' + str(idx) + ')' + file_extension
    return file_name_full
