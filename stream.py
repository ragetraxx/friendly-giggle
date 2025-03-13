import datetime
import os
import subprocess
import shlex
import time
import xml.etree.ElementTree as ET
import requests

# Constants
EPG_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/refs/heads/main/epg.xml"
EPG_FILE = "epg.xml"
OMDB_API_KEY = "a3b171bc"
OMDB_URL = "http://www.omdbapi.com/?apikey=" + OMDB_API_KEY
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_REFRESH_INTERVAL = 21600  # 6 hours

def download_epg():
    """Download the latest EPG file or generate a default one if missing."""
    try:
        response = requests.get(EPG_URL, timeout=10)
        if response.status_code == 200:
            with open(EPG_FILE, "wb") as f:
                f.write(response.content)
            print("✅ EPG file updated successfully!")
            return
    except requests.RequestException as e:
        print(f"❌ ERROR: Failed to download EPG - {e}")

    # If download fails or file is missing, generate a default EPG
    if not os.path.exists(EPG_FILE):
        print("⚠️ WARNING: EPG file missing! Generating a default one...")
        generate_default_epg()

def generate_default_epg():
    """Generate a default EPG with placeholder movies."""
    now = datetime.datetime.utcnow()
    epg = ET.Element("tv")

    for i in range(5):  # Generate 5 placeholder movies
        start_time = now + datetime.timedelta(hours=i * 2)
        stop_time = start_time + datetime.timedelta(hours=2)

        programme = ET.SubElement(epg, "programme", {
            "start": start_time.strftime("%Y%m%d%H%M%S +0000"),
            "stop": stop_time.strftime("%Y%m%d%H%M%S +0000"),
            "channel": "bihm"
        })

        ET.SubElement(programme, "title").text = f"Movie {i+1} (Placeholder)"
        ET.SubElement(programme, "desc").text = "Placeholder Movie Description"
        ET.SubElement(programme, "icon", {"src": "https://via.placeholder.com/150"})
        ET.SubElement(programme, "link").text = "https://example.com/stream"

    tree = ET.ElementTree(epg)
    tree.write(EPG_FILE, encoding="UTF-8", xml_declaration=True)
    print("✅ Default EPG generated!")

def main():
    """Main loop to ensure EPG exists and update it every 6 hours."""
    last_epg_update = 0

    while True:
        now = time.time()

        if now - last_epg_update >= EPG_REFRESH_INTERVAL:
            download_epg()
            last_epg_update = now

        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    main()
