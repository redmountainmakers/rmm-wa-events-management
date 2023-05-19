from wa_events_functions import*

wa_api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API

group_id = 749571

email_list =  get_contact_list(access_token,group_id)

