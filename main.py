import subprocess
from wa_events_functions import*

current_ics_url = 'https://redmountainmakers.org/resources/Events_Conversion/redmountainmakers_events.ics'

#Specifies the local file paths for files to be saved locally on the Actions runner
ics_current_path = 'redmountainmakers_events.ics'
wa_ics_path = 'wa_events.ics'
output_ics_path = 'rmm_events.ics'
today = datetime.today().strftime('%Y-%m%d')
save_path_with_date = ics_current_path[:-4] + f"_{today}.ics"
archive_ics_path = "archive/" + save_path_with_date
log_file_path = f"archive/event_update.log"
bham365_events = "bham365.csv"

download_ics_file(current_ics_url,ics_current_path)#Downloads the current ics file from the RMM website

wa_api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API


upcoming_events = get_upcoming_events(access_token) #Gets the list of upcoming events and data from the WA API
create_ics_file(upcoming_events,wa_ics_path)#creates the ics file from the WA API data

process_calendar(ics_current_path, wa_ics_path, output_ics_path,log_file_path)#Deletes old events, adds new events, and updates changed events
upload_to_aws(output_ics_path)

#print(upcoming_events)

events_to_csv(upcoming_events,bham365_events)

#pushes the log file, archive ics file, and the updated ics file to the git repo
subprocess.run(['git', 'add', output_ics_path])
subprocess.run(['git', 'add', archive_ics_path])
subprocess.run(['git', 'add', log_file_path])
subprocess.run(['git', 'add', bham365_events])
subprocess.run(['git', 'commit', '-m', 'Added updated .ics files'])
subprocess.run(['git', 'push'])
