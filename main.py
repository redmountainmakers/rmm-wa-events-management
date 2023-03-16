import os
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

#download_and_commit()
upcoming_events = get_upcoming_events(access_token)
account_id = get_account_id(access_token)
folder_id = 'Events_Conversion'
ics_file = create_ics_file(upcoming_events)
file_name = 'test.ics'
list_folders(access_token, account_id)
#upload_file_to_wildapricot(access_token, account_id, folder_id, file_name, ics_file)
