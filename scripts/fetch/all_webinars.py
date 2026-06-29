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

output_directory_path = Path(config["output_folder_path"])
output_filename = config["get_all_webinars"]["output_filename"]
output_file_path = output_directory_path / output_filename

endpoint = config["get_all_webinars"]["api_endpoint"]
request_data = {
    "api_key": API_KEY
}

print("sending a POST request to", endpoint, "with data", request_data)
print("\nwaiting for a response...\n")

response = requests.post(endpoint, request_data)

print("response received with status code", response.status_code)

response_json = response.json()
formatted_response = json.dumps(response_json, indent=4)

print("successfully decoded response to JSON")

# create the output directory if it doesn't exist already
output_directory_path.mkdir(parents=True, exist_ok=True)

print(f"\nwriting response to {output_file_path}...\n")

with open(output_file_path, "w") as file:
    file.write(formatted_response)

print("done!")
