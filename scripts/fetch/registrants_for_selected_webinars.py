import os
from pathlib import Path
import json
from datetime import datetime
import time

from dotenv import load_dotenv
import tomllib
import requests

# adds all key-value pairs in the `.env` file to `os.environ`
load_dotenv()

API_KEY = os.environ["WEBINARJAM_API_KEY"]

with open("config.toml", "rb") as file:
    config = tomllib.load(file)

OUTPUT_DIRECTORY_PATH = Path(config["output_folder_path"])

WEBINARS_LIST_FILE_PATH = OUTPUT_DIRECTORY_PATH / config["fetch_all_webinars"]["output_filename"]

with open(WEBINARS_LIST_FILE_PATH) as file:
    webinars = json.load(file)["webinars"]

webinar_count = len(webinars)

print(f"Loaded information for all {webinar_count} webinars from {WEBINARS_LIST_FILE_PATH}.")
print()

fetch_config = config["fetch_registrants_for_selected_webinars"]

ENDPOINT = fetch_config["api_endpoint"]

INCLUDE_YEAR = fetch_config["include_year"]
EXCLUDED_KEYWORDS = fetch_config["exclude_webinars_with_names_containing"]

# (see https://docs.python.org/3/library/datetime.html#format-codes)
# the time string in the registrant data looks like this:
# Tuesday, 17 Mar 2026, 4:00 PM
STRPTIME_FORMAT = "%A, %d %b %Y, %I:%M %p"

registrants = {}

for webinar in webinars:
    webinar_name = webinar["name"]
    webinar_id = webinar["webinar_id"]

    # there could be one or multiple schedules for a single webinar
    webinar_first_schedule = webinar["schedules"][0]

    try:
        webinar_first_schedule_datetime = datetime.strptime(webinar_first_schedule, STRPTIME_FORMAT)
    except ValueError:
        # some webinars will have a schedule of 'Right now', in which case there is no other data that can be used to determine the webinar's date
        print(f"Skipped webinar '{webinar_name}' because its date '{webinar_first_schedule}' is unparseable.")
        continue

    # skip webinars that are not in the specified year
    if webinar_first_schedule_datetime.year != INCLUDE_YEAR:
        print(f"Skipped webinar '{webinar_name}' because it was not held in the year {INCLUDE_YEAR}.")
        continue

    # a `continue` inside this `for` loop has no effect on the outer `for webinar in webinars` loop
    skip = False
    for keyword in EXCLUDED_KEYWORDS:
        # check the keyword against the webinar name in lowercase
        if keyword in webinar_name.lower():
            print(f"Skipped webinar '{webinar_name}' because its name contains '{keyword}'.")
            skip = True
    if skip is True:
        continue

    current_page = 1
    registrants_of_current_webinar = []

    # the WebinarJam API does not return all registrants at once, but instead splits them into pages
    # which means that a new POST request has to be sent for each page
    print()
    while True:
        print(f"[page {current_page}] Fetching registrants for webinar '{webinar_name}' (ID: {webinar_id})...")

        request_data = {
            "api_key": API_KEY,
            "webinar_id": webinar_id,
            "page": current_page
        }

        response = requests.post(ENDPOINT, request_data)

        response_json = response.json()
        registrants_of_current_webinar += response_json["registrants"]["data"]

        # prevent exceeding the WebinarJam API's limit of 20 API calls per second
        time.sleep(0.06)

        if (response_json["registrants"]["next_page_url"] is None):
            break

        current_page += 1

    registrants[webinar_id] = registrants_of_current_webinar
    print()

output_filename = config["fetch_registrants_for_selected_webinars"]["output_filename"]
output_file_path = OUTPUT_DIRECTORY_PATH / output_filename

with open(output_file_path, "w") as file:
    formatted_registrants = json.dumps(registrants, indent=4)
    file.write(formatted_registrants)

print()
print(f"Successfully written the registrant data of {len(registrants)} webinars to {output_file_path}.")
