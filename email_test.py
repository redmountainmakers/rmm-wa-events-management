from wa_events_functions import*

wa_api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API

get_contact_list(access_token,749571)
