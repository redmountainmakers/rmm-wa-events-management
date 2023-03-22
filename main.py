import os
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

current_events = 'https://github.com/Creidhne86/wa_events_2_ics/blob/main/redmountainmakers_events.ics'

download_and_commit(current_events)#Downloads the list of current events and archives them in a repo archive
upcoming_events = get_upcoming_events(access_token) #Gets the list of upcoming events from the WA API
ics_current_path = 'redmountainmakers_events.ics'
wa_ics_path = 'wa_events.ics'
new_ics_path = 'updated_events.ics'
output_ics_path = 'rmm_events.ics'

create_ics_file(upcoming_events,wa_ics_path)#creates the ics file from the WA API data
delete_past_events(ics_current_path,new_ics_path)
add_additional_events(ics_current_path, wa_ics_path, new_ics_path)
update_fields(new_ics_path, wa_ics_path,output_ics_path)

commit_and_push(output_ics_path)