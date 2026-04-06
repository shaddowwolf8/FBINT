# FBINT - Social Media Username Scanner & Visualization

FBINT is a Python tool to scan social media platforms for usernames, fetch profile information, extract locations, and visualize connections in an interactive graph with optional map integration.

---

## Features

- Generate permutations of a full name to create potential usernames.
- Scan popular social media platforms for username availability:
  - Instagram, TikTok, Twitter, GitHub, Reddit, Twitch, Pinterest, Tumblr, Snapchat, YouTube, Facebook, LinkedIn, VK, Weibo
- Extract profile images and textual information.
- Attempt to geolocate profiles based on text or IP.
- Score found profiles based on relevance to the target name.
- Generate interactive HTML graphs using **pyvis**, with toggleable map view using **Leaflet**.
- Colorful terminal output using **colorama**.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shaddowwolf8/FBINT.git
cd FBINT
2. Install the required dependencies:
pip install -r requirements.txt
3. Usage
Run the script:
python fbint.py
Enter the target name when prompted.
Wait for the scan to complete — found profiles will be displayed in the terminal.
After scanning, an interactive HTML graph will open in your default browser.
Toggle between GRAPH view and MAP view.
Hover over nodes to see profile info and score.
Click nodes to see profile images (if available).
Configuration
SITES list in the script contains the supported social media platforms.
SEPARATORS list defines separators used when generating username permutations.
HEADERS can be customized to change the User-Agent for HTTP requests.
ThreadPoolExecutor manages concurrency — adjust max_workers for performance.
Dependencies
requests
 – HTTP requests
beautifulsoup4
 – HTML parsing
pyvis
 – Network graph visualization
colorama
 – Colored terminal output

All required dependencies are listed in requirements.txt.

Notes
This tool is intended for educational and ethical use only.
Excessive or unauthorized scanning of social media platforms may violate their Terms of Service.
Some profiles may be private or blocked; not all usernames will be discoverable.
Geolocation is approximate and may not reflect the exact location of the user.
