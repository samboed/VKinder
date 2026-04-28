import logging
import requests

from src.vk_api.logger import NAME_VK_API_LOGGER


logger = logging.getLogger(NAME_VK_API_LOGGER)


def process_get_request(url: str,
                        params: dict = None,
                        headers: dict = None,
                        expect_status_code: int = 200) -> dict | bool:
    if not headers:
        headers = {}
    if not params:
        params = {}

    try:
        response = requests.get(url, headers=headers, params=params)
    except requests.exceptions.RequestException as ex:
        logger.error(f"{url=}, {ex}")
        return False

    if response.status_code != expect_status_code:
        logger.error(f"{url=}, Expected <{expect_status_code}>, received <{response.status_code}>")
        return False

    error_json_data = response.json().get("error")
    if error_json_data:
        error_msg = error_json_data["error_msg"]
        logger.error(f"{url=}, {error_msg}")
        return False

    return response.json()