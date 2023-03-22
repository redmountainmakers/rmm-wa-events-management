import subprocess
from wa_events_functions import*

api_key = os.environ.get("API_KEY")
access_token = get_access_token(api_key)

current_ics_url = 'https://redmountainmakers.org/resources/Events_Conversion/redmountainmakers_events.ics'

upcoming_events = get_upcoming_events(access_token) #Gets the list of upcoming events from the WA API
ics_current_path = 'redmountainmakers_events.ics'
wa_ics_path = 'wa_events.ics'
output_ics_path = 'rmm_events.ics'
today = datetime.today().strftime('%Y-%m%d')
save_path_with_date = ics_current_path[:-4] + f"_{today}.ics"
archive_ics_path = "archive/" + save_path_with_date
log_file_path = f"archive/event_update_{today}.log"

download_ics_file(current_ics_url,ics_current_path)
create_ics_file(upcoming_events,wa_ics_path)#creates the ics file from the WA API data
process_calendar(ics_current_path, wa_ics_path, output_ics_path,log_file_path)


subprocess.run(['git', 'add', output_ics_path])
subprocess.run(['git', 'add', archive_ics_path])
subprocess.run(['git', 'add', log_file_path])
subprocess.run(['git', 'commit', '-m', 'Added updated .ics files'])
subprocess.run(['git', 'push'])
