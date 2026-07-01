import os
import json
import time
import logging

from dotenv import load_dotenv
import requests

from config.GlobalConfig import GlobalConfig
from config.WebinarListConfig import WebinarListConfig
from config.RegistrantsByWebinarConfig import RegistrantsByWebinarConfig
from utils import confirm_if_overwriting_file

logging.basicConfig(level=logging.INFO)

load_dotenv()

WEBINAR_LIST_FILE_PATH = GlobalConfig.OUTPUT_DIRECTORY_PATH / WebinarListConfig.OUTPUT_FILENAME

logging.info(f"opening the file {WEBINAR_LIST_FILE_PATH}...")
with open(GlobalConfig.OUTPUT_DIRECTORY_PATH / WebinarListConfig.OUTPUT_FILENAME) as file:
    webinar_list = json.load(file)

logging.info(f"loaded {len(webinar_list)} webinars from {WEBINAR_LIST_FILE_PATH}")

OUTPUT_SUBDIRECTORY_PATH = GlobalConfig.OUTPUT_DIRECTORY_PATH / RegistrantsByWebinarConfig.OUTPUT_SUBDIRECTORY

# create the output sub-directory if it doesn't yet exist
OUTPUT_SUBDIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

print()
skip_fetching_if_file_exists = input(f"skip fetching registrants for a webinar if a file for the webinar already exists in {OUTPUT_SUBDIRECTORY_PATH}? [y/n] ").lower().strip()
print()

skip_fetching_if_file_exists = True if skip_fetching_if_file_exists == "y" or skip_fetching_if_file_exists == "yes" else False

for webinar in webinar_list:
    webinar_name = webinar["name"]
    webinar_id = webinar["webinar_id"]

    current_file_path = OUTPUT_SUBDIRECTORY_PATH / f"{webinar_id}.json"

    if os.path.isfile(current_file_path) is True and skip_fetching_if_file_exists is True:
        logging.info(f"skipped webinar '{webinar_name}' because {current_file_path} already exists")
        continue

    current_page = 1
    registrants_of_current_webinar = []

    logging.info("")
    logging.info(f"fetching registrants for webinar '{webinar_name}' (ID: {webinar_id}, date: {webinar["schedules"][0]})...")
    # the WebinarJam API does not return all registrants at once, but instead splits them into pages
    # which means that a new POST request has to be sent for each page
    while True:
        logging.info(f"[{webinar_id}: page {current_page}]")

        request_data = {
            "api_key": os.environ["WEBINARJAM_API_KEY"],
            "webinar_id": webinar_id,
            "page": current_page
        }

        response = requests.post(RegistrantsByWebinarConfig.API_ENDPOINT, request_data)

        response_json = response.json()
        registrants_of_current_webinar += response_json["registrants"]["data"]

        # prevent exceeding the WebinarJam API's limit of 20 API calls per second
        time.sleep(0.06)

        if (response_json["registrants"]["next_page_url"] is None):
            break

        current_page += 1


    confirm_if_overwriting_file(current_file_path, exit_if_no_overwrite=False)

    with open(current_file_path, "w") as file:
        formatted_registrants_of_current_webinar = json.dumps(registrants_of_current_webinar, indent=4)
        file.write(formatted_registrants_of_current_webinar)

    logging.info(f"wrote {len(formatted_registrants_of_current_webinar)} characters representing {len(registrants_of_current_webinar)} registrants to {current_file_path}")
