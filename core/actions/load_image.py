import os
import re
from common import EXPECTED_FORMATS, MAX_FILE_SIZE
from database import save_to_database

def check_load_image_rules(file_info) -> tuple[bool, list[str]]:
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


def load_image_save_to_database(user_id: int, file_id: str, hashtags: list[str]) -> tuple[bool, list[str]]:
    ok = save_to_database(user_id, file_id, hashtags)

    errors = []
    if not ok:
        errors.append("@topShizoid - failed to bind image data with tags")
    return (ok, errors)


def extract_hashtags(prompt: str):
    prompt = prompt.lower()
    hashtags = list(map(lambda x: x[1:], re.findall(r'#\w+', prompt)))

    return hashtags