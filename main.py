import os
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

#download_and_commit()
upcoming_events = get_upcoming_events(access_token)
ics_file = create_ics_file(upcoming_events)
save_ics_file(ics_file)
commit_and_push("rmm_events.ics")