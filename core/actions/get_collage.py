from typing import BinaryIO

COLLAGE = ''    # collage as byte array
COLLAGE_GIVEN_SUCCESSFULLY = True

def help(message) -> str:
    return "get collage called"


def process(message) -> str:
    '''
    Here processing checks of tags, possibility of
    collage building, censor and so on
    if all is OK -> return success message
    :param message: telebot.types.Message
    :return: str (text answer to user)
    '''
    global COLLAGE

    prompt = message.text
    tags = parse_tags(prompt)

    errors = list[str]()
    if is_valid_prompt(tags, errors):
        answer = "success string :: get_collage :: process(message)"
        COLLAGE = build_collage(tags)

    else:
        error_string = '\n'.join(errors)
        answer = error_string

    return answer


def parse_tags(prompt) -> list[str]:
    pass


def is_valid_prompt(tags: list[str], errors: list[str]) -> bool:
    # TODO: maybe given too much tags > 5 maybe
    return True

    limit = 5
    ok = True

    if len(tags) > limit:
        errors.append("Слишком много тегов, попробуйте меньше")
        ok = False

    return ok


def is_possible_collage(tags: list[str], errors: list[str]) -> bool:
    '''
    this function checks count of same photos
    to making collage
    :param tags: given from user's text
    :param errors: list reference, which contains all errors
    during processing and returns it as answer
    :return: true if we have photos, false if don't
    '''
    # TODO: DB searching logic
    pass


def build_collage(tags: list[str]) -> BinaryIO:
    '''
    It's get_collage's core, here building an image
    as binary buffer. After return this data takes
    telebot.bot.send_photo(...) function
    :param tags: list of #tags
    :return: binary buffered collage
    '''
    # choose photos
    # creates new file
    # building
    # sending
    return open(r"C:\Users\home\Pictures\derpy-hooves-pony-wallpaper-preview.jpg", 'rb')


def get_instance() -> BinaryIO:
    return COLLAGE


def is_ok() -> bool:
    return COLLAGE_GIVEN_SUCCESSFULLY