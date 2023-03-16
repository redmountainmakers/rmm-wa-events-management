import os
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

#download_and_commit()
ical_data = get_upcoming_events(access_token)
file_name = 'test.ics'
upload_file_to_wildapricot(api_key,file_name)
