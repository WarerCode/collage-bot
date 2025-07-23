import os
import re
from core.common import EXPECTED_FORMATS, MAX_FILE_SIZE
from core.database import save_to_database

"""
LoadImageBuffer is a special class which contains
file_info attributes for saving in db
'save_to_database' & 'LoadImageBuffer.__init__' signature are same 
"""
class LoadImageBuffer:
    def __init__(self, user_id: int=0, file_id: str=''):
        self.user_id = user_id
        self.file_id = file_id

    def load(self, user_id: int, file_id: str):
        self.user_id = user_id
        self.file_id = file_id

# static buffer for db
LOAD_IMAGE_BUFFER = LoadImageBuffer(0, '')

def check_load_image_rules(file_info) -> (bool, list[str]):
    file_path = file_info.file_path
    format = os.path.splitext(file_path)[1].lower()
    file_size = file_info.file_size

    errors = []
    res = True
    if format not in EXPECTED_FORMATS:
        errors.append("@topShizoid2010 - unexpected or undefined format checking failed msg :: common.py")
        res = False
    if file_size >= MAX_FILE_SIZE:
        errors.append("@topShizoid2010 - too large file msg :: common.py")
        res = False

    return (res, errors)


def save_to_buffer(user_id: int, file_id: str):
    global LOAD_IMAGE_BUFFER
    LOAD_IMAGE_BUFFER.load(user_id, file_id)


def bind_buffer_data_with_tags(hashtags: list[str]) -> (bool, list[str]):
    ok = save_to_database(LOAD_IMAGE_BUFFER.user_id,
                     LOAD_IMAGE_BUFFER.file_id,
                     hashtags)

    errors = []
    if not ok:
        errors.append("@topShizoid - failed to bind image data with tags")
    return (ok, errors)


def extract_hashtags(prompt: str):
    hashtags = re.findall(r'#\w+', prompt)
    return hashtags