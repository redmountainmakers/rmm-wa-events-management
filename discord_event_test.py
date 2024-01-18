import os
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
    finally:
        await client.close()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = client.get_guild(SERVER_ID)
    if guild is None:
        print("Discord server not found. Check the SERVER_ID.")
        await client.close()
        return

    discord_events = guild.scheduled_events()
    discord_event_identifiers = {(discord_event.name, discord_event.start_time.strftime('%Y-%m-%d')) for discord_event in discord_events}

    for wa_event in upcoming_wa_events:
        wa_event_name = wa_event['name']
        wa_start_time = dateutil.parser.isoparse(wa_event['StartDate'])
        wa_end_time = dateutil.parser.isoparse(wa_event['EndDate'])
        wa_event_location = wa_event['url']

        # Create a unique identifier for the external event
        event_identifier = (wa_event_name, wa_start_time.strftime('%Y-%m-%d'))

        # Check if the event already exists in Discord
        if event_identifier in discord_event_identifiers:
            print(f"Event '{wa_event_name}' on {wa_start_time.strftime('%Y-%m-%d')} already exists in Discord. Skipping...")
            continue

        await create_scheduled_event(guild, wa_event_name, wa_event_name, wa_start_time, wa_end_time, wa_event_location)

    await client.close()
    
client.run(DISCORD_BOT_TOKEN)
