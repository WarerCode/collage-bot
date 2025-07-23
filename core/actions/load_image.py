from core.common import * # bot phrases
from core.database import * #saving

IMAGE_LOADED_SUCCESSFULLY = True
IMAGE   = ''
FILE_ID = ''

def process(message) -> str:    # TODO: JaneeWaterlemonka !!!! it's Your, babe vvv
    """
    This function parsing tags and binds
    photo from buffer with it
    after photo with tags saving in DB
    :param message: telegram.user.message
    :return: status response
    """
    global IMAGE, FILE_ID

    chat_id = message.chat.id
    prompt  = message.text
    tags    = parse_tags(prompt)

    errors = []
    if is_valid_prompt(tags, errors) and is_ok():
        save_image_to_database(chat_id, str(FILE_ID))
        ok = save_to_database(chat_id, FILE_ID, tags)
        increment_tag_popularity(tags)

    else:
        print(f"invalid prompt or troubles with buffer from {chat_id}, file {FILE_ID}")
        return '\n\n'.join(errors)

    return SUCCESS_MSG


def parse_tags(prompt) -> list[str]:
    return [prompt]


def is_valid_prompt(tags: list[str], errors: list[str]) -> bool:
    # TODO: maybe given too much tags > 5 maybe
    return True

    limit = 5
    ok = True

    if len(tags) > limit:
        errors.append("Слишком много тегов, попробуйте меньше")
        ok = False

    return ok


def save_to_buffer(photo, file_id) -> bool:
    """
    Сохраняет фото в буфер и проверяет, что данные не пустые
    :param photo: байтовый массив с изображением
    :return: True, если данные сохранены корректно, False - если нет
    """
    global IMAGE_LOADED_SUCCESSFULLY, IMAGE, FILE_ID

    if photo and isinstance(photo, (bytes, bytearray)) and len(photo) > 0:
        IMAGE = photo
        FILE_ID = file_id
        IMAGE_LOADED_SUCCESSFULLY = True
    else:
        IMAGE_LOADED_SUCCESSFULLY = False

    return IMAGE_LOADED_SUCCESSFULLY


def is_ok() -> bool:
    """
    :return: current load image action context status
    """
    return IMAGE_LOADED_SUCCESSFULLY