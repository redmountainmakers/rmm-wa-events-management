import subprocess
from wa_events_functions import*


current_ics_url = 'https://redmountainmakers.org/resources/Events_Conversion/bham_now_export.ics'

#Specifies the local file paths for files to be saved locally on the Actions runner
current_ics_path = 'current_bham_now_export.ics'
wa_api_ics_path = 'wa_api_events.ics'
new_ics_path = 'new_bham_now_export.ics'
log_file_path = f"event_update.log"
aws_file_name = 'rmm_events.ics'
bham365_events = "bham365.csv"

#WA API auth setup
wa_api_key = os.environ.get("WA_API_KEY")
wa_username = "bot@redmountainmakers.org"
wa_password = os.environ.get("WA_BOT_ACCT_PW")
access_token = get_access_token(wa_api_key)

#Downloads the current ics file from the RMM website
download_ics_file(current_ics_url,current_ics_path)

#Gets the list of upcoming events and data from the WA API
filter_tags = ['bham now']
upcoming_events = get_events(access_token,filter_tags=filter_tags) 

#Creates the ics file from the WA API data
create_ics_file(upcoming_events,wa_api_ics_path)

#Deletes old events, adds new events, and updates changed events
process_calendar(current_ics_path, wa_api_ics_path, new_ics_path,log_file_path)

upload_to_wa(wa_username=wa_username, wa_password=wa_password, src_file_path=new_ics_path, dst_file_url=current_ics_url)

events_to_csv(upcoming_events,bham365_events)

print(upcoming_events)

# with open(bham365_events, mode='r', encoding='utf-8') as csv_file:
#     reader = csv.DictReader(csv_file)
#     for row in reader:
#         print(f"Event Name: {row['Event Name']}, Start Date: {row['Start Date']}")