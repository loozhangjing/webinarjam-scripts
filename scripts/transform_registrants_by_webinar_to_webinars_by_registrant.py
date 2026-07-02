import json

from registrants_by_webinar_ids import registrants_by_webinar_ids

registrants_for_selected_webinars = registrants_by_webinar_ids([1228, 1229])

print(json.dumps(registrants_for_selected_webinars, indent=4))
