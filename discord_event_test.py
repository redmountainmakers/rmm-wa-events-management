import os
import discord
import datetime as dt
from discord.utils import utcnow
from wa_events_functions import* 

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SERVER_ID = int(os.getenv("SERVER_ID"))
wa_api_key = os.environ.get("WA_API_KEY")#Gets the API key from the environment variables
access_token = get_access_token(wa_api_key)#Gets the access token from the WA API



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

    event_name = "Test Event"
    event_description = "This is a test event"
    event_start = utcnow() + dt.timedelta(days=100)  # Adjust as needed
    event_end = event_start + dt.timedelta(hours=2)
    event_location = "https://example.com/event"  # Replace with your actual event URL or location

    await create_scheduled_event(guild, event_name, event_description, event_start, event_end, event_location)

    await client.close()

upcoming_events = get_events(access_token)
for event in upcoming_events:
    print(event)

print(upcoming_events)
client.run(DISCORD_BOT_TOKEN)
