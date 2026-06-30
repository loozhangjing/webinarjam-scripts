import os
from pathlib import Path
import json

from dotenv import load_dotenv
import tomllib
import requests

# adds all key-value pairs in the `.env` file to `os.environ`
load_dotenv()

API_KEY = os.environ["WEBINARJAM_API_KEY"]

with open("config.toml", "rb") as file:
    config = tomllib.load(file)

OUTPUT_DIRECTORY_PATH = Path(config["output_folder"])
OUTPUT_FILE_PATH = OUTPUT_DIRECTORY_PATH / config["fetch_webinar_list"]["output_filename"]

ENDPOINT = config["fetch_webinar_list"]["api_endpoint"]
request_data = {
    "api_key": API_KEY
}

print(f"Fetching the list of webinars from {ENDPOINT}...")

response = requests.post(ENDPOINT, request_data)

response_json = response.json()
webinars = response_json["webinars"]

# create the output directory if it doesn't exist already
OUTPUT_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE_PATH, "w") as file:
    formatted_response = json.dumps(webinars, indent=4)
    file.write(formatted_response)

print()
print(f"Successfully written the data of {len(webinars)} webinars to {OUTPUT_FILE_PATH}.")
