from pathlib import Path
import json

import tomllib

with open("config.toml", "rb") as file:
    config = tomllib.load(file)

OUTPUT_DIRECTORY_PATH = Path(config["output_folder_path"])

REGISTRANTS_PER_WEBINAR_FILE_PATH = OUTPUT_DIRECTORY_PATH / config["fetch_registrants_for_selected_webinars"]["output_filename"]

with open(REGISTRANTS_PER_WEBINAR_FILE_PATH) as file:
    registrants_per_webinar = json.load(file)

print(f"Loaded {len(registrants_per_webinar)} webinars from {REGISTRANTS_PER_WEBINAR_FILE_PATH}.")

# in this dictionary, registrants are first-class citizens (instead of webinars as in `registrants_per_webinar`)
unique_registrants = {}

for webinar_id, webinar_registrants in registrants_per_webinar.items():
    for registrant in webinar_registrants:
        email = registrant["email"]

        # if this registrant doesn't yet exist in the dict, add them
        if email not in unique_registrants:
            unique_registrants[email] = {
                "first_name": registrant["first_name"],
                "last_name": registrant["last_name"],
                "phone_country_code": registrant["phone_country_code"],
                "phone_number": registrant["phone_number"],
                "total_registered": 0,
                "total_attended": 0
            }

        # ever registrant that exists under a webinar has *registered* for that webinar but might not have *attended* its live session (maybe they watched a replay)
        unique_registrants[email]["total_registered"] += 1

        unique_registrants[email][webinar_id] = {
            "registered": True,
            "attended": False
        }

        if registrant["attended_live"] == "Yes":
            unique_registrants[email]["total_attended"] += 1
            unique_registrants[email][webinar_id]["attended"] = True

OUTPUT_FILE_PATH = OUTPUT_DIRECTORY_PATH / config["transform_into_webinars_per_registrant"]["output_filename"]

with open(OUTPUT_FILE_PATH, "w") as file:
    formatted_webinars_per_registrant = json.dumps(unique_registrants, indent=4)
    file.write(formatted_webinars_per_registrant)

print()
print(f"Written the data of {len(unique_registrants)} unique registrants to {OUTPUT_FILE_PATH}.")
