import os
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

current_events = 'https://github.com/Creidhne86/wa_events_2_ics/blob/main/archive/redmountainmakers_events_2023-0316.ics'

download_and_commit(current_events)
upcoming_events = get_upcoming_events(access_token)
wa_ics_file = create_ics_file(upcoming_events)
ics_current_path = 'redmountainmakers_events_2023-0316.ics'
new_ics = add_additional_events(ics_current_path, wa_ics_file)
new_ics = update_fields(ics_current_path, new_ics)
save_ics_file(new_ics)
commit_and_push("rmm_events.ics")