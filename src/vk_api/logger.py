import logging


NAME_VK_API_LOGGER = "vk-api"


def init_logger():
    logger = logging.getLogger(NAME_VK_API_LOGGER)
    logger.setLevel(logging.ERROR)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
