from wa_events_functions import*

wa_api_key = os.environ.get("WA_API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API

group_id = 749571

#if today is monday timescale = weekly
#if today is logic for monthly timescale = timescale = monthly
#if both conditions are met, combine?
current_datetime = datetime.now(timezone.utc)
start_datetime = current_datetime + timedelta(days=2, hours = 7) #By default the script runs at 5:30pm CST on fridays, so I've offset it to pick up any events starting on Monday morning at 12:30 AM
end_datetime = start_datetime + timedelta(days=8) #sets the end date one week from the "offset datetime" to get a full week of events, it should run through the following Monday's events.

timescale_info = start_datetime.strftime("%m/%d/%Y") +" through "+ end_datetime.strftime("%m/%d/%Y")
email_subject = f"RMM Events from {timescale_info}"
template_email_file_path = 'event_email_template.html'
html_template = read_template_file(template_email_file_path)

event_list = get_events(access_token,start_datetime,end_datetime)
event_list_html = parse_events_html(event_list)

filled_template = fill_email_template(timescale_info,event_list_html,html_template)

email_list =  get_contact_list(access_token,group_id)


for contact_id in email_list:
    send_email(access_token,email_subject,filled_template, contact_id)

