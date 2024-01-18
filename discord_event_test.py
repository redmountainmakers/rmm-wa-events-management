import os
import discord
import datetime as dt

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))



intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)  # Fetch the channel object
    guild = client.get_guild(SERVER_ID)
    
    # Define event details
    event_name = "Test Event"
    event_description = "Join us for a fun night of gaming!"
    event_start = dt.datetime(2025, 1, 25, 20, 0)  # Example start time
    event_end = dt.datetime(2025, 1, 25, 22, 0)  # Example end time
    #event_location = CHANNEL_ID  # Assuming it's an online event in a specific channel

    # Create event (this is a conceptual example)
    await guild.create_scheduled_event(name=event_name, description=event_description,
                                       start_time=event_start, end_time=event_end)

    await client.close()

# Log in to Discord runs the on_ready function
client.run(DISCORD_BOT_TOKEN)