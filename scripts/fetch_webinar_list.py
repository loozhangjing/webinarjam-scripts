import os
import json
import logging

from dotenv import load_dotenv
import requests

from config.GlobalConfig import GlobalConfig
from config.WebinarListConfig import WebinarListConfig
from utils import confirm_if_overwriting_file

logging.basicConfig(level=logging.INFO)

load_dotenv()
request_data = {
    "api_key": os.environ["WEBINARJAM_API_KEY"]
}

logging.info(f"fetching the list of webinars from {WebinarListConfig.API_ENDPOINT}...")

response = requests.post(WebinarListConfig.API_ENDPOINT, request_data)
logging.info("response received")

response_json = response.json()
logging.info("response converted to JSON")

webinars = response_json["webinars"]
logging.info(f"there are {len(webinars)} webinars")

# create the output directory if it doesn't yet exist
GlobalConfig.OUTPUT_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE_PATH = GlobalConfig.OUTPUT_DIRECTORY_PATH / WebinarListConfig.OUTPUT_FILENAME

confirm_if_overwriting_file(OUTPUT_FILE_PATH)

with open(OUTPUT_FILE_PATH, "w") as file:
    formatted_response = json.dumps(webinars, indent=4)
    file.write(formatted_response)

logging.info(f"wrote {len(formatted_response)} characters to {OUTPUT_FILE_PATH}")
