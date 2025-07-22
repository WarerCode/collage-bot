from core.common import * # bot phrases

IMAGE_LOADED_SUCCESSFULLY = True

def process(message) -> str:
    """
    This function parsing tags and binds
    photo from buffer with it
    after photo with tags saving in DB
    :param message: telegram.user.message
    :return: status response
    """
    return SUCCESS_MSG


def save_to_buffer(photo) -> bool:
    """
    set IMAGE_LOADED_SUCCESSFULLY in True/False
    :param photo: byte array raw data
    :return: True if saved ok, False - not ok
    """
    global IMAGE_LOADED_SUCCESSFULLY
    IMAGE_LOADED_SUCCESSFULLY = True

    return True


def is_ok() -> bool:
    """
    :return: current load image action context status
    """
    return IMAGE_LOADED_SUCCESSFULLY