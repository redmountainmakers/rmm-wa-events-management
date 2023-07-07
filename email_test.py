from wa_events_functions import*

wa_api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API

group_id = 749571

#if today is monday timescale = weekly
#if today is logic for monthly timescale = timescale = monthly
#if both conditions are met, combine?
current_datetime = datetime.now(timezone.utc)
one_week = current_datetime + timedelta(weeks=1)

timescale_info = "Events from 7/7/2023 through 7/14/2023"
email_subject = "RMM Events from 7/7/2023 through 7/14/2023"
template_email_file_path = 'event_email_template.html'
html_template = read_template_file(template_email_file_path)

event_list = get_events(access_token,current_datetime,one_week)
print(event_list)
event_list_html = parse_events_html(event_list)

filled_template = fill_email_template(timescale_info,event_list_html,html_template)

email_list =  get_contact_list(access_token,group_id)


for contact_id in email_list:
    send_email(access_token,email_subject,filled_template, contact_id)

