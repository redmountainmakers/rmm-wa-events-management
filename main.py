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

wa_ics_file = create_ics_file(upcoming_events)#creates the ics file from the WA API data
with open(wa_ics_path, 'wb') as f:#writes the ics data locally
    f.write(wa_ics_file)

#new_ics = delete_old_events(ics_current_path, new_ics_path)
#with open(wa_ics_path, 'wb') as f:#writes the ics data locally
#    f.write(new_ics)



new_ics = add_additional_events(ics_current_path, wa_ics_path)
with open(new_ics_path, 'wb') as f:#writes the ics data locally
    f.write(new_ics)
new_ics = update_fields(new_ics_path, wa_ics_path)
save_ics_file(new_ics)#saves the final file as rmm events.ics
commit_and_push("rmm_events.ics")