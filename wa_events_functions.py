import os
import uuid
import pytz
import base64
import requests
import logging
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timezone

def download_ics_file(url, save_path):
    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {save_path}")

        # Save a second copy with today's date in the filename
        today = datetime.today().strftime('%Y-%m%d')
        archive_folder = 'archive'
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
        save_path_with_date = os.path.join(archive_folder, save_path[:-4] + f"_{today}.ics")
        with open(save_path_with_date, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {save_path_with_date}")
    else:
        print(f"Failed to download file: {response.status_code}")

def get_access_token(api_key):
    
    """Obtains and returns an access token for the Wild Apricot API."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    auth_url = 'https://oauth.wildapricot.org/auth/token'

    # Encode the API key in base64 format
    encoded_key = base64.b64encode(f'APIKEY:{api_key}'.encode()).decode()

    # Set the headers for authentication
    auth_headers = {
        'Authorization': f'Basic {encoded_key}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Obtain the access token
    auth_data = {'grant_type': 'client_credentials', 'scope': 'auto'}
    auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
    access_token = auth_response.json()['access_token']

    return access_token

def get_account_id(access_token):
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    return account_response.json()[0]['Id']

def get_upcoming_events(access_token):
    """Retrieves upcoming public event data from the Wild Apricot API and returns a list of events."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    account_id = account_response.json()[0]['Id']

    # Get the current date and time
    current_datetime = datetime.now(timezone.utc)

    # Make an API request to retrieve upcoming event data
    events_response = requests.get(f'{api_base_url}/accounts/{account_id}/Events', headers=headers)
    events = events_response.json()['Events']

    # Filter out events that have already ended, are not visible to the public, or have "private" in the title
    upcoming_events = [event for event in events if event.get('StartDate') is not None and
                       datetime.fromisoformat(event['StartDate'][:-1]+'0') >= current_datetime and
                       event.get('AccessLevel') == 'Public' and
                       'private' not in event.get('Name', '').lower()]

    return upcoming_events

def get_wa_description(event_id):
    """Retrieves the contents of the boxBodyContentOuterContainer div for the specified event ID."""
    # Construct the URL for the event page
    url = f'https://redmountainmakers.org/event-{event_id}'

    # Make a request to the event page and retrieve the HTML
    response = requests.get(url)
    html = response.text

    # Replace &nbsp; with Unicode non-breaking space
    html = html.replace('&nbsp;', ' ')

    # Parse the HTML with BeautifulSoup and find the boxBodyContentOuterContainer div
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='inner gadgetEventEditableArea')

    # Replace image URLs that start with "/resources" to include "https://www.redmountainmakers.org"
    for img in div.find_all('img', src=True):
        if img['src'].startswith('/resources'):
            img['src'] = f'https://www.redmountainmakers.org{img["src"]}'

    # Extract the contents of the div
    contents = str(div.prettify())

    return contents

def create_ics_file(events, file_path):
    """Creates and writes an iCalendar file containing the events to the given file path."""
    # Create a new iCalendar file
    cal = Calendar()

    # Set the original timezone
    original_tz = pytz.timezone('America/Chicago')

    # Loop through each event in the Wild Apricot data
    for event in events:
        # Extract the relevant information from the event
        event_id = event['Id']
        event_title = event['Name']
        description_leading_text = f'Click here to register:\n\n<href>https://www.redmountainmakers.org/event-{event_id}</href>'
        event_description = description_leading_text + get_wa_description(event_id)
        event_start = datetime.fromisoformat(event['StartDate'][:-1] + '0').replace(tzinfo=None)
        event_start = original_tz.localize(event_start).astimezone(pytz.utc)
        event_end = datetime.fromisoformat(event['EndDate'][:-1] + '0').replace(tzinfo=None)
        event_end = original_tz.localize(event_end).astimezone(pytz.utc)
        event_location = event['Location']
        event_tag = event['Tags'][0].capitalize() if event['Tags'] else ''
        if event_tag:
            event_title = f'{event_tag} Class: {event_title}'

        # Create a new event in the iCalendar file
        event = Event()
        event.add('uid', str(uuid.uuid4())) # Add a UID for the event
        event.add('event_id', event_id)
        event.add('summary', event_title)
        event.add('description', event_description)
        event.add('dtstart', event_start)
        if event_end:
            event.add('dtend', event_end)
        event.add('location', event_location)
        event.add('prodid', '-//Wild Apricot//wildapricot.org//')

        # Add the event to the iCalendar file
        cal.add_component(event)

    # Write the iCalendar file to disk
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())

    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(file_path)}')

def delete_past_events(ics_current_path, ics_output_path, log_file_path):
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Read the current .ics file
    with open(ics_current_path, 'rb') as ics_current_file:
        ics_current = Calendar.from_ical(ics_current_file.read())

    # Get the current date and time in the UTC timezone
    utc_now = datetime.now(tz=pytz.utc)

    # Loop through each event in the calendar
    for component in ics_current.walk():
        if component.name == "VEVENT":
            # Get the start time of the event in the UTC timezone
            start_time = component.get("DTSTART").dt.astimezone(pytz.utc)

            # Check if the event has already occurred
            if start_time < utc_now:
                # Remove the event from the calendar
                event_id = component.get("EVENT_ID")
                ics_current.subcomponents.remove(component)
                logger.info(f'Removed event with ID {event_id}')

    # Write the iCalendar file to disk
    with open(ics_output_path, 'wb') as f:
        f.write(ics_current.to_ical())

    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(ics_output_path)}')

def update_fields(ics_current_path, ics_latest_path, ics_output_path, log_file_path):
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    with open(ics_current_path, 'rb') as ics_current_file:
        ics_current = Calendar.from_ical(ics_current_file.read())

    with open(ics_latest_path, 'rb') as ics_latest_file:
        ics_latest = Calendar.from_ical(ics_latest_file.read())

    latest_events = {}
    for event in ics_latest.walk('VEVENT'):
        event_id = event.get('EVENT_ID')
        if event_id:
            latest_events[event_id] = event

    for event in ics_current.walk('VEVENT'):
        event_id = event.get('EVENT_ID')
        if event_id and event_id in latest_events:
            latest_event = latest_events[event_id]
            fields_to_update = ['SUMMARY', 'DTSTART', 'DTEND', 'DESCRIPTION', 'LOCATION']

            for field in fields_to_update:
                if latest_event.get(field) != event.get(field):
                    logger.info(f'{field} has changed for {event_id}')
                if latest_event.get(field) is not None:
                    event[field] = latest_event[field]

    with open(ics_output_path, 'wb') as f:
        f.write(ics_current.to_ical())
        
    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(ics_output_path)}')


    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(ics_output_path)}')

def add_additional_events(ics_current_path, ics_latest_path, ics_output_path, log_file_path):
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    with open(ics_current_path, 'rb') as ics_current_file:
        ics_current = Calendar.from_ical(ics_current_file.read())

    with open(ics_latest_path, 'rb') as ics_latest_file:
        ics_latest = Calendar.from_ical(ics_latest_file.read())

    current_event_ids = {event.get('EVENT_ID') for event in ics_current.walk('VEVENT') if event.get('EVENT_ID')}
    latest_event_ids = {event.get('EVENT_ID') for event in ics_latest.walk('VEVENT') if event.get('EVENT_ID')}

    additional_events = latest_event_ids - current_event_ids
    for event_id in additional_events:
        new_event = next((event for event in ics_latest.walk('VEVENT') if event.get('EVENT_ID') == event_id), None)
        if new_event:
            ics_current.add_component(new_event)
            logger.info(f'Added event_id {event_id}')

    with open(ics_output_path, 'wb') as f:
        f.write(ics_current.to_ical())

    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(ics_output_path)}')

def save_ics_file(ics_content, file_name="rmm_events.ics"):
    with open(file_name, "wb") as f:
        f.write(ics_content)

def process_calendar(ics_current_path, ics_latest_path, ics_output_path, log_file_path):
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Read the current and latest .ics files
    with open(ics_current_path, 'rb') as ics_current_file:
        ics_current = Calendar.from_ical(ics_current_file.read())

    with open(ics_latest_path, 'rb') as ics_latest_file:
        ics_latest = Calendar.from_ical(ics_latest_file.read())

    # Get the current date and time in the UTC timezone
    utc_now = datetime.now(tz=pytz.utc)

    latest_events = {}
    for event in ics_latest.walk('VEVENT'):
        event_id = event.get('EVENT_ID')
        if event_id:
            latest_events[event_id] = event

    current_event_ids = set()
    for event in ics_current.walk('VEVENT'):
        event_id = event.get('EVENT_ID')

        # Delete past events
        start_time = event.get("DTSTART").dt.astimezone(pytz.utc)
        if start_time < utc_now:
            ics_current.subcomponents.remove(event)
            logger.info(f'Removed event with ID {event_id}')
            continue

        current_event_ids.add(event_id)

        # Update fields
        if event_id and event_id in latest_events:
            latest_event = latest_events[event_id]
            fields_to_update = ['SUMMARY', 'DTSTART', 'DTEND', 'DESCRIPTION', 'LOCATION']

            for field in fields_to_update:
                if latest_event.get(field) != event.get(field):
                    logger.info(f'{field} has changed for {event_id}')
                if latest_event.get(field) is not None:
                    event[field] = latest_event[field]

    # Add additional events
    latest_event_ids = set(latest_events.keys())
    additional_events = latest_event_ids - current_event_ids
    for event_id in additional_events:
        new_event = latest_events.get(event_id)
        if new_event:
            ics_current.add_component(new_event)
            logger.info(f'Added event_id {event_id}')

    # Write the iCalendar file to disk
    with open(ics_output_path, 'wb') as f:
        f.write(ics_current.to_ical())

    # Print the file path for confirmation
    print(f'iCalendar file written to {os.path.abspath(ics_output_path)}')


