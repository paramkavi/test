import requests
import re
import os

# Ensure the playlists directory exists
os.makedirs("playlists", exist_ok=True)

# URL of the raw M3U file
url = "https://raw.githubusercontent.com/aseanic/aseanic.github.io/refs/heads/main/tv"

# Fetch the content from the URL
response = requests.get(url)
if response.status_code != 200:
    print(f"Failed to fetch URL: {response.status_code}")
    exit(1)

# Initialize the M3U content
m3u_content = "#EXTM3U\n"

# Parse the content line by line
lines = response.text.splitlines()
current_channel = {}
for line in lines:
    line = line.strip()
    if line.startswith("#EXTINF:"):
        # Extract channel details from #EXTINF line
        match = re.match(r'#EXTINF:-?\d+\s*(.*?),(.+)', line)
        if match:
            attributes, channel_name = match.groups()
            # Parse attributes for group-title, tvg-id, and tvg-logo
            group_title = re.search(r'group-title="([^"]+)"', attributes)
            tvg_id = re.search(r'tvg-id="([^"]+)"', attributes)
            tvg_logo = re.search(r'tvg-logo="([^"]+)"', attributes)
            current_channel = {
                "name": channel_name.strip(),
                "group_title": group_title.group(1) if group_title else "",
                "tvg_id": tvg_id.group(1) if tvg_id else "",
                "tvg_logo": tvg_logo.group(1) if tvg_logo else ""
            }
    elif line and not line.startswith("#"):
        # This is the URL for the channel
        current_channel["url"] = line
        # Generate M3U entry
        attributes = f'group-title="{current_channel["group_title"]}" tvg-id="{current_channel["tvg_id"]}" tvg-logo="{current_channel["tvg_logo"]}"'
        m3u_content += f'#EXTINF:-1 {attributes},{current_channel["name"]}\n'
        m3u_content += f'{current_channel["url"]}\n'
        # Reset current channel
        current_channel = {}

# Save the M3U content to a file in the playlists directory
output_path = "playlists/extracted_playlist.m3u"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(m3u_content)

print(f"M3U playlist generated successfully as '{output_path}'")
