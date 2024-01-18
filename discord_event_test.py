import os
import discord
import datetime as dt

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SERVER_ID = 567080925884710912
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))



intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # Debugging: Print SERVER_ID
    print(f"SERVER_ID: {SERVER_ID}")

    guild = client.get_guild(SERVER_ID)
    print(f"Guild: {guild}")  # Debugging: Print guild object

    # Check if guild is found
    if guild is None:
        print("Guild not found. Check the SERVER_ID.")
        await client.close()
        return

    # Define event details
    event_name = "Test Event"
    event_description = "This is a test event"
    event_start = dt.datetime(2025, 1, 25, 20, 0)  # Example start time
    event_end = dt.datetime(2025, 1, 25, 22, 0)  # Example end time

    # Create event
    await guild.create_scheduled_event(name=event_name, description=event_description, start_time=event_start, end_time=event_end)

    await client.close()

# Log in to Discord runs the on_ready function
client.run(DISCORD_BOT_TOKEN)