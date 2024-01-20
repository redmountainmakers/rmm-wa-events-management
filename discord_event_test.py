import os
import asyncio
import discord
import dateutil.parser
import datetime as dt
from discord.utils import utcnow
from wa_events_functions import* 

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SERVER_ID = int(os.getenv("SERVER_ID"))
wa_api_key = os.environ.get("WA_API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API
upcoming_wa_events = get_events(access_token)

#print(f"{len(upcoming_wa_events)} upcoming events found:")
#for event in upcoming_wa_events:
#    print(event)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def create_scheduled_event(guild, event_name, event_description, event_start, event_end, event_location):
    try:
        await guild.create_scheduled_event(
            name=event_name,
            description=event_description,
            start_time=event_start,
            end_time=event_end,
            entity_type=discord.EntityType.external,
            location=event_location,
            privacy_level=discord.PrivacyLevel.guild_only
        )
        print("Event created successfully.")
    except Exception as e:
        print(f"Error creating event: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = client.get_guild(SERVER_ID)
    if guild is None:
        print("Discord server not found. Check the SERVER_ID.")
        await client.close()
        return

    discord_events = guild.scheduled_events
    discord_event_details = {
    event.description: (event.id, event.name, event.start_time, event.end_time)
    for event in discord_events
    if event.description and event.description.startswith('https://redmountainmakers.org/event-')
    }

    wa_event_descriptions = set()
    for wa_event in upcoming_wa_events:
        wa_event_name = wa_event['Name']
        wa_start_time = dateutil.parser.isoparse(wa_event['StartDate'])
        wa_end_time = dateutil.parser.isoparse(wa_event['EndDate'])
        wa_event_id = wa_event['Id']
        wa_event_location = wa_event['Location']


        wa_event_description = f'https://redmountainmakers.org/event-{wa_event_id}'

        # Add to the set of Wild Apricot event descriptions
        wa_event_descriptions.add(wa_event_description)

        # Check for existing event in Discord
        if wa_event_description in discord_event_details:
            discord_event_id, discord_event_name, discord_start_time, discord_end_time = discord_event_details[wa_event_description]

            # Check for changes in title, time, or duration
            changed = False
            if wa_event_name != discord_event_name:
                print(f"Event '{wa_event_name}'  description has been updated. Updating in Discord...")
                changed=True
            if wa_start_time != discord_start_time:
                print(f"Event '{wa_event_name}' start time has been updated. Updating in Discord...")
                changed=True
            if wa_end_time != discord_end_time:
                print(f"Event '{wa_event_name}' end time has been updated. Updating in Discord...")
                changed=True

            if not changed:
                print(f"Event '{wa_event_name}' already exists in Discord and no changes were detected. Skipping...")
                continue
            else:
                print(f"Event '{wa_event_name}' already exists in Discord but was changed. Updating in Discord...")
                await guild.get_scheduled_event(discord_event_id).edit(
                    name=wa_event_name,
                    description=wa_event_description,
                    start_time=wa_start_time,
                    end_time=wa_end_time
                )
        try:
            await create_scheduled_event(guild, wa_event_name, wa_event_description, wa_start_time, wa_end_time, wa_event_location)
            print(f"Event {wa_event_description} created successfully.")
        except Exception as e:
            print(f"Error creating event {wa_event_description}: {e}")
        await asyncio.sleep(1)

    discord_events_to_remove = set(discord_event_details.keys()) - wa_event_descriptions
    for event_description in discord_events_to_remove:
        discord_event_id = discord_event_details[event_description][0]
        try:
            await guild.delete_guild_scheduled_event(SERVER_ID,discord_event_id)
            print(f"Event with URL {event_description} removed successfully.")
        except Exception as e:
            print(f"Error removing event with URL {event_description}: {e}")

    await client.close()
    
client.run(DISCORD_BOT_TOKEN)