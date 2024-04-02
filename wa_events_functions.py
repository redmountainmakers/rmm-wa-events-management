import os
import csv
import uuid
import pytz
import json
import boto3
import base64
import requests
import logging
from bs4 import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar, Event
from datetime import datetime, timezone, timedelta
from requests.auth import HTTPDigestAuth

def download_ics_file(url, save_path):
    """
    Downloads an .ics file from the specified URL and saves it to the specified path. 

    Args:
        url (str): The URL to download the file from.
        save_path (str): The path to save the downloaded file.

    Returns:
        None
    """

    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File saved to {save_path}")
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

def get_events(access_token,start_date=None, end_date=None,filter_tags=[]):
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

    
    #Create a filter query to only get a response based on upcoming events
    filter_query = f"StartDate gt {current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    # If start_date and/or end_date are given, adjust the filter_query accordingly
    if start_date:
        filter_query += f" and StartDate ge {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        
    if end_date:
        filter_query += f" and EndDate le {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"


    # Make an API request to retrieve event data
    events_response = requests.get(f'{api_base_url}/accounts/{account_id}/Events?$filter={filter_query}', headers=headers)
    
    events = events_response.json()['Events']

    # Filter out events that have already ended, are not visible to the public, or have "private" in the title
    events = [event for event in events if ((not filter_tags or any(tag in event.get('Tags', []) for tag in filter_tags)) and
                       event.get('AccessLevel') == 'Public' and
                       'private' not in event.get('Name', '').lower())]
    
    return events

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
        if 'summer' in event_title.lower():
            event_title = "RMM " + event_title
        description_leading_text = f'Click here to register:\n\n<a href = https://www.redmountainmakers.org/event-{event_id}>https://www.redmountainmakers.org/event-{event_id}</a>'
        event_description = description_leading_text + get_wa_description(event_id)
        event_start = datetime.fromisoformat(event['StartDate'][:-1] + '0').replace(tzinfo=None)
        event_start = original_tz.localize(event_start).astimezone(pytz.utc)
        event_end = datetime.fromisoformat(event['EndDate'][:-1] + '0').replace(tzinfo=None)
        event_end = original_tz.localize(event_end).astimezone(pytz.utc)
        event_location = event['Location'].upper()#converts the event location to uppercase
        ignore_tags = ['bham now', 'social', 'summer series']  # Define the tags to ignore

        event_tag = None
        if event.get('Tags'):  # Check if tags exist
            for tag in event['Tags']:  # Iterate over all tags
                print(tag.lower())
                print(tag.lower() not in ignore_tags)
                if tag.lower() not in ignore_tags:  # If the tag is not in the ignore list
                    event_tag = tag.capitalize()  # Assign it to event_tag
                    break  # Stop iterating as we've found a valid tag

        if event_tag:  # If we found a valid tag
            event_title = f'{event_tag} Class: {event_title}'  # Prepend it to the event title


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

def process_calendar(ics_current_path, ics_latest_path, ics_output_path, log_file_path):
    """
    Processes calendar updates by reading two ics files, comparing them, and updating them accordingly.

    :param ics_current_path: A string representing the path to the current ics file.
    :param ics_latest_path: A string representing the path to the latest ics file.
    :param ics_output_path: A string representing the path to the output ics file.
    :param log_file_path: A string representing the path to the log file.
    """

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

    logger.info(f'Starting to process calendar updates')

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
    for event in ics_current.subcomponents[:]:  # use a copy for iteration
        if event.name != 'VEVENT':
            continue

        event_id = event.get('EVENT_ID')

        # Delete past events
        start_time = event.get("dtstart").dt.astimezone(pytz.utc)
        if start_time < utc_now:
            ics_current.subcomponents.remove(event)
            logger.info(f'Removed past event with ID {event_id}')

        #delete removed events *checks for events that are no longer in the ics_current and removes them*
        elif event_id not in latest_events:
            ics_current.subcomponents.remove(event)
            logger.info(f'Removed event with ID {event_id} as it is not in the latest calendar')
        else:
            current_event_ids.add(event_id)

    # Update fields
    for event_id in current_event_ids:
        event = next(e for e in ics_current.subcomponents if e.name == 'VEVENT' and e.get('EVENT_ID') == event_id)
        latest_event = latest_events[event_id]
        fields_to_update = ['SUMMARY', 'DTSTART', 'DTEND', 'DESCRIPTION', 'LOCATION']

        for field in fields_to_update:
            if latest_event.get(field) != event.get(field):
                logger.info(f'{field} has changed for {event_id}')
            if latest_event.get(field) is not None:
                event[field.lower()] = latest_event[field]

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

def events_to_csv(events, file_path):
    headers = [
        "Event Name", "Org Name", "Venue Name", "Event Description", "Event Category",
        "Event Sub-Category", "Event URL", "Event Phone", "Event Email", "Admission",
        "Ticket URL", "Start Date", "End Date", "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday", "Image", "Contact Name", "Contact Phone", "Contact Email"
    ]

    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for event in events:
            start_date = datetime.fromisoformat(event['StartDate'].replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(event['EndDate'].replace("Z", "+00:00"))

            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekday_start_time = {day: "" for day in weekdays}
            weekday_start_time[weekdays[start_date.weekday()]] = start_date.strftime("%-I:%M %p")
            html_input = get_wa_description(event['Id'])

            soup = BeautifulSoup(html_input, 'html.parser')
            event_image = None
            
            event_id = event['Id']
            url = f'https://redmountainmakers.org/event-{event_id}'

            img_tag = soup.find('img')
            if img_tag:
                event_image = img_tag.get('src')

            writer.writerow({
                "Event Name": event["Name"],
                "Org Name": "Red Mountain Makers",
                "Venue Name": "Red Mountain Makers HWP",
                "Event Description": get_wa_description(event['Id']),
                "Event Category": "Classes + Lectures",
                "Event Sub-Category": "",
                "Event URL": url,
                "Event Phone": "205-588-4077",
                "Event Email": "classes@redmountainmakers.org",
                "Admission": "",
                "Ticket URL": url,
                "Start Date": start_date.strftime("%m/%d/%Y"),
                "End Date": end_date.strftime("%m/%d/%Y"),
                **weekday_start_time,
                "Image": event_image,
                "Contact Name": "Carla Gadson",
                "Contact Phone": "205-588-4077",
                "Contact Email": "Carla@redmountainmakers.org"
            })

def upload_to_aws(src_file_path, dest_file_path):
    aws_access_key = os.environ['AWS_ACCESS_KEY']
    aws_secret_key = os.environ['AWS_SECRET_KEY']

    s3_client = boto3.client('s3', aws_access_key_id = aws_access_key, aws_secret_access_key = aws_secret_key)
    
    bucket_name = 'rmm-events-ics'
    object_key = f'{dest_file_path}'

    # Open the file that you want to update
    with open(src_file_path, 'rb') as f:
        # Upload the file to S3
        s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=f, ACL='public-read')
    
    # Print a message to let the user know that the file has been updated
    print('The file has been updated successfully.')

def print_event_titles_from_ics(file_path):
    # Open the .ics file
    with open(file_path, 'rb') as ics_file:
        ics_content = Calendar.from_ical(ics_file.read())

        # Iterate over each event in the calendar
        for component in ics_content.walk('VEVENT'):
            event_title = component.get('SUMMARY')

            # Print the event title
            print(event_title)

def get_contact_info(contact_id, access_token):
    """Retrieves the email address and first name of a contact given a contact ID."""
    api_base_url = 'https://api.wildapricot.org/v2.1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve the contact details
    contact_response = requests.get(f'{api_base_url}/accounts/{account_id}/contacts/{contact_id}', headers=headers)
    if contact_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve contact details. Status code: {contact_response.status_code}')
        return

    contact_details = contact_response.json()

    # Get the email address, first name, and membership status from the contact details
    email = contact_details.get('Email', 'Unknown')
    first_name = contact_details.get('FirstName', 'Unknown')
    membership_enabled = contact_details.get('MembershipEnabled', False)

    return email, first_name, contact_id, membership_enabled

def send_email(access_token,email_subject,body, contact_id,):


    """Sends a test email using the Wild Apricot API."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']
    
    contact_info = get_contact_info(contact_id,access_token)
    
    first_name = contact_info[1]
    email = contact_info[0]
    
    # Prepare email data
    email_data = {
        "Subject": email_subject,
        "Body": body,
        "ReplyToAddress": "secretary@redmountainmakers.org",
        "ReplyToName": "Red Mountain Makers",
        "Recipients": [
            {
                "Id": contact_id,
                "Type": "IndividualContactRecipient",
                "Name": first_name,
                "Email": email,
            }
        ],
    }


    # Make an API request to send the email
    send_email_response = requests.post(f'{api_base_url}/rpc/{account_id}/email/SendEmail', headers=headers, json=email_data)
    
    if send_email_response.status_code != 200:
        logging.error(f'Error: Unable to send email. Status code: {send_email_response.status_code}')
        return

def get_contact_list(access_token,group_id):
    """Retrieves a list of contact id's based on an input group id"""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return
    
    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve the contact details
    contact_response = requests.get(f'{api_base_url}/accounts/{account_id}/membergroups/{group_id}', headers=headers)
    if contact_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve contact details. Status code: {contact_response.status_code}')
        return

    # Initialize an empty list to hold the contact IDs
    contact_ids_list = []

    group_info = contact_response.json()

    contact_ids_list.extend(group_info['ContactIds'])
    #print(contact_ids_list)

    return contact_ids_list
    
def fill_email_template(timescale_info,event_list,template):
    return template.format(timescale_info=timescale_info,event_list=event_list)

def parse_events_html(events):
    
    events.sort(key=lambda e: parse(e['StartDate']))

    output_list = []
    base_url = "https://redmountainmakers.org/event-"

    for event in events:
        event_id = event['Id']
        print(event_id)
        event_name = event['Name']
        event_url = base_url + str(event_id)

        # Convert StartDate to "MM/DD/YYYY HH:MM AM/PM" format in CST
        start_date_str = event['StartDate']
        start_date_dt = parse(start_date_str)

        # Convert to Central Standard Time
        cst = pytz.timezone('US/Central')
        start_date_dt = start_date_dt.astimezone(cst)

        formatted_date_time = start_date_dt.strftime("%m/%d/%Y %I:%M %p")

        html_element = f'''
        <table class="text_block block-2" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
            <tr>
                <td class="pad" style="padding-bottom:10px;padding-left:45px;padding-right:45px;padding-top:10px;">
                    <div style="font-family: sans-serif">
                        <div style="font-size: 12px; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #f2103b; line-height: 1.2;">
                            <p style="margin: 0; font-size: 14px; text-align: left; mso-line-height-alt: 16.8px; letter-spacing: 6px;"><a href="{event_url}" style="color:#f00">{event_name}</a><br><span style="color:#ffffff;">{formatted_date_time}</span></p>
                        </div>
                    </div>
                </td>
            </tr>
        </table>'''
        print(html_element)

        output_list.append(html_element)

    
    
    output_html = "\n".join(output_list)
    print(output_html)

    return output_html

def read_template_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def upload_to_wa(wa_username, wa_password, src_file_path, dst_file_url):
    
    # Make sure the directory exists on the webserver manually or update this function.. todo   
    #  
    #dst_file_url example: https://www.redmountainmakers.org/resources/Pictures/test.png

    headers = {
        'Content-type': 'application/octet-stream',
    }
    upload_response = requests.put(dst_file_url, data=open(src_file_path, 'rb'), headers=headers, auth=HTTPDigestAuth(wa_username, wa_password))
    try:
        upload_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        raise SystemExit(e)
