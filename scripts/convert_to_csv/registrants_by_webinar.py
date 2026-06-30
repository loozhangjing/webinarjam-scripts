from pathlib import Path
import json

import tomllib

with open("config.toml", "rb") as file:
    config = tomllib.load(file)

OUTPUT_DIRECTORY_PATH = Path(config["output_folder"])

REGISTRANTS_BY_WEBINAR_FILE_PATH = OUTPUT_DIRECTORY_PATH / config["fetch_registrants_by_webinar"]["output_filename"]

csv_output_directory_path = OUTPUT_DIRECTORY_PATH / Path(config["convert_registrant_data_to_csv"]["output_subfolder"])

with open(REGISTRANTS_BY_WEBINAR_FILE_PATH) as file:
    registrants = json.load(file)

csv_first_line = config["convert_registrant_data_to_csv"]["first_line"]
json_keys = config["convert_registrant_data_to_csv"]["json_keys"]

# create the csv output directory if it doesn't exist already
csv_output_directory_path.mkdir(parents=True, exist_ok=True)

for webinar_id, registrants_of_this_webinar in registrants.items():
    contents = csv_first_line

    for registrant in registrants_of_this_webinar:
        contents += "\n"

        for key in json_keys:
            value = registrant[key]

            # don't write `None` or `""` to the file
            if value is not None and value != "":
                # surround the value in double quotes so that
                # any commas within aren't interpreted as a new value
                contents += f"\"{registrant[key]}\","
            else:
                contents += ","

        contents += f"{registrant["country"]["name"]},"

        if registrant["state"] is not None:
            contents += registrant["state"]["name"]

    filename = f"{registrants_of_this_webinar[0]["webinar"]}.csv"
    file_path = csv_output_directory_path / filename

    # the "w+" mode will create a file if it doesn't exist
    with open(file_path, "w+") as file:
        file.write(contents)

    print("created and wrote to", file_path)
