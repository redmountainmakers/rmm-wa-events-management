# RMM_WA_Events_Management
This code publishes RMM Events from Wild Apricot to a cloud AWS file in .ics format. It also creates a .csv template for importing to BHam365, syncs events with Discord, and sends weekly emails to the marketing team with upcoming events.

## Usage
The "Events to .ics" workflow runs automatically overnight at 2AM CST via github actions, and it runs update_ics.py. Log files and historical .ics data are stored in the Archive folder of this repository 
The "Email Events" workflow runs automatically weekly at at 5:30PM CST via github actions, and it runs email_events.py.
the Discord Events sync workflow runs automatically overnight at 2AM CST via github actions, it Imports the upcoming events handler from the wa_events_functions.py library, compares that list with similar events alreay posted to discord

Most functions are contained within the #wa_events_functions.py

## Description

1. **Event Retrieval**: Fetches upcoming event data from Wild Apricot. Only events with the "BHam Now" tag, are retrieved. Past events, and private events are automatically filtered from the retrieval.
2. **Event Reformatting**: Events are reformatted to be passed to a .ics, and a unique uuid is created. Titles are updated to "{event_tag} class: {class name}", for example "Intro to cutting boards" is renamed to "Woodworking Class: Intro to cutting boards"
3. **Event Publishing**: Publishes the event data to a cloud-based AWS file in the .ics format, enabling easy sharing and integration with various calendar applications. https://rmm-events-ics.s3.us-east-2.amazonaws.com/rmm_events.ics
4. **CSV Template Creation**: Generates a .csv template suitable for importing event data into BHam365. (This is not actively used)

### Events to .ics workflow

1. **Email Notifications**: Sends out weekly email notifications to the marketing team  detailing the upcoming events to aid in promotional efforts.
2. **Email list** Defined in wild apricot admin console members->groups->Marketing class list

### Discord Events sync workflow
1.**General Functionality*: Imports the upcoming events handler from the wa_events_functions.py library, compares that list with similar events alreay posted to discord
2. **Added events**: Adds events that are not already on discord
3. **Changed Events**: Checks if an event is already on discord (Indirectly via the wild apricot Event_ID, and updates the Title, Description (URL), start time, end time, or location, if those changed on wild_apricot
4. **Deleted Events**: If there is an event on discord that is no longer in wild apricot, it gets deleted from discord


## Contribution
Feel free to fork the project and submit pull requests for any enhancements.

## License
[MIT License](LICENSE)

## Contact
For more information, contact the RMM general email at [secretary@redmountainmakers.org](mailto:secretary@redmountainmakers.org) and it will be forwarded appropriately.
