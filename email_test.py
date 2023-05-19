from wa_events_functions import*

wa_api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API

group_id = 749571

if today is monday timescale = weekly
if today is logic for monthly timescale = timescale = monthly
if both conditions are met, combine?

event_list = get_events(timescale)
filled_template = populate_email_template(event_list,timescale)

email_list =  get_contact_list(access_token,group_id)



for contact_id in email_list:
    send_email(access_token,filled_template, contact_id)

