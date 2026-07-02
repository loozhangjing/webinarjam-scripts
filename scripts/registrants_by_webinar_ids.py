from typing import List
import json
import logging

from config.GlobalConfig import GlobalConfig
from config.RegistrantsByWebinarConfig import RegistrantsByWebinarConfig

logging.basicConfig(level=logging.INFO)

def registrants_by_webinar_ids(webinar_ids: List[int]):
    registrants_by_webinar = []

    for id in webinar_ids:
        filename = f"{id}.json"
        file_path = GlobalConfig.OUTPUT_DIRECTORY_PATH / RegistrantsByWebinarConfig.OUTPUT_SUBDIRECTORY / filename

        logging.info(f"attempting to read from {file_path}")

        with open(file_path) as file:
            logging.info(f"attempting to parse the contents of {file_path} as JSON")

            registrants_of_current_webinar = json.load(file)

        # concatenate the previous registrants and the current registrants
        registrants_by_webinar.extend(registrants_of_current_webinar)

    return registrants_by_webinar
