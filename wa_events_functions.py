import os
import subprocess
from datetime import datetime
import requests

def download_and_commit():
    # Download the file
    url = 'https://redmountainmakers.org/resources/Events_Conversion/redmountainmakers_events.ics'
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save the file with today's date in the filename
        today = datetime.today().strftime('%Y-%m%d')
        archive_folder = 'archive'
        filename = f'redmountainmakers_events_{today}.ics'
        file_path = os.path.join(archive_folder, filename)
        
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Commit and push the changes
        subprocess.run(['git', 'add', file_path])
        subprocess.run(['git', 'commit', '-m', f'Add {filename} to archive'])
        subprocess.run(['git', 'push', 'origin', 'main'])
    else:
        print(f"Failed to download file: {response.status_code}")

if __name__ == "__main__":
    download_and_commit()
