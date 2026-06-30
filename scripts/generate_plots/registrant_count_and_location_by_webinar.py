from pathlib import Path
import json
from datetime import datetime

import tomllib
import matplotlib
import matplotlib.pyplot as plt

with open("config.toml", "rb") as file:
    config = tomllib.load(file)

OUTPUT_DIRECTORY_PATH = Path(config["output_folder"])

REGISTRANTS_FILENAME = config["fetch_registrants_by_webinar"]["output_filename"]
REGISTRANTS_FILE_PATH = OUTPUT_DIRECTORY_PATH / REGISTRANTS_FILENAME

PLOTS_OUTPUT_DIRECTORY_PATH = OUTPUT_DIRECTORY_PATH / config["plots"]["output_subfolder"]

with open(REGISTRANTS_FILE_PATH) as file:
    registrants = json.load(file)

# create the csv output directory if it doesn't exist already
PLOTS_OUTPUT_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

webinar_names_with_dates = []
webinar_ids = []
registrant_counts = []
registrant_locations = {}

# see https://docs.python.org/3/library/datetime.html#format-codes
# the time string in the registrant data looks like this:
# Tue, 17 Mar 2026, 04:00 PM
STRPTIME_FORMAT = "%a, %d %b %Y, %I:%M %p"

for webinar_id, registrants_of_this_webinar in registrants.items():
    webinar_name = registrants_of_this_webinar[0]["webinar"]
    webinar_datetime = datetime.strptime(registrants_of_this_webinar[0]["schedule"], STRPTIME_FORMAT)
    registrant_count = len(registrants_of_this_webinar)

    number_attended_live = sum(r["attended_live"] == "Yes" for r in registrants_of_this_webinar)
    proportion_attended_live = number_attended_live / registrant_count

    for registrant in registrants_of_this_webinar:
        country = registrant["country"]["name"]
        if country == "Malaysia" and registrant["state"] is not None:
            state = registrant["state"]["name"]
            if state not in registrant_locations:
                registrant_locations[state] = 0
            registrant_locations[state] += 1
        else:
            country = f"[no state specified] {country}"
            if country not in registrant_locations:
                registrant_locations[country] = 0
            registrant_locations[country] += 1

    webinar_ids.append(webinar_id)
    webinar_names_with_dates.append(f"{webinar_name} [{webinar_datetime}]")
    registrant_counts.append(registrant_count)

sorted_pairs = sorted(zip(registrant_counts, webinar_names_with_dates))
sorted_registrant_counts, sorted_webinar_names = map(list, zip(*sorted_pairs))

matplotlib.rc("font", family="Noto Sans CJK SC")

plt.style.use('_mpl-gallery')

fig, ax = plt.subplots()

ax.barh(sorted_webinar_names, sorted_registrant_counts)
ax.set_ylabel("Webinar Name")
ax.set_xlabel("Number of registrants")

ax.tick_params(axis="y", labelsize=4)

ax.figure.savefig(PLOTS_OUTPUT_DIRECTORY_PATH / "matplotlib.pdf", bbox_inches="tight")

fig, ax = plt.subplots()

ax.barh(list(registrant_locations.keys()), list(registrant_locations.values()))
ax.set_ylabel("State / Country")
ax.set_xlabel("Number of registrants")

ax.tick_params(axis="y", labelsize=4)

ax.figure.savefig(PLOTS_OUTPUT_DIRECTORY_PATH / "matplotlib2.pdf", bbox_inches="tight")
