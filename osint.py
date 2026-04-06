import requests, itertools, time, re, webbrowser, os, socket, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from pyvis.network import Network
from colorama import Fore, Style, init

init(autoreset=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (FBINT)"}

SEPARATORS = ["", ".", "_", "-", "__"]

SITES = [
    ("Instagram", "https://www.instagram.com/{}"),
    ("TikTok", "https://www.tiktok.com/@{}"),
    ("Twitter", "https://twitter.com/{}"),
    ("GitHub", "https://github.com/{}"),
    ("Reddit", "https://www.reddit.com/user/{}"),
    ("Twitch", "https://www.twitch.tv/{}"),
    ("Pinterest", "https://www.pinterest.com/{}"),
    ("Tumblr", "https://{}.tumblr.com"),
    ("Snapchat", "https://www.snapchat.com/add/{}"),
    ("YouTube", "https://www.youtube.com/@{}"),
    ("Facebook", "https://www.facebook.com/{}"),
    ("LinkedIn", "https://www.linkedin.com/in/{}"),
    ("VK", "https://vk.com/{}"),
    ("Weibo", "https://weibo.com/{}"),
]

# ---------------- BANNER ----------------
def banner():
    print(Fore.MAGENTA + """
███████╗██████╗ ██╗███╗   ██╗████████╗
██╔════╝██╔══██╗██║████╗  ██║╚══██╔══╝
█████╗  ██████╔╝██║██╔██╗ ██║   ██║   
██╔══╝  ██╔══██╗██║██║╚██╗██║   ██║   
██║     ██████╔╝██║██║ ╚████║   ██║   
╚═╝     ╚═════╝ ╚═╝╚═╝  ╚═══╝   ╚═╝   

            FBINT
""" + Style.RESET_ALL)

# ---------------- GEO ----------------
def extract_location(text):
    patterns = [
        r"based in ([a-zA-Z ,]+)",
        r"lives in ([a-zA-Z ,]+)",
        r"from ([a-zA-Z ,]+)",
        r"location[:\- ]+([a-zA-Z ,]+)",
        r"📍 ([a-zA-Z ,]+)",
        r"📌 ([a-zA-Z ,]+)"
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)[:60]
    return None

def geocode(location):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None

def ip_geo(domain):
    try:
        ip = socket.gethostbyname(domain)
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if r["status"] == "success":
            return r["lat"], r["lon"]
    except:
        pass
    return None

# ---------------- IMAGE ----------------
def get_img(html):
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", property="og:image")
    return meta["content"] if meta else None

# ---------------- USERNAMES ----------------
def generate(name):
    parts = name.lower().split()
    out = set()

    for perm in itertools.permutations(parts):
        for sep in SEPARATORS:
            base = sep.join(perm)
            out.add(base)
            out.add(base[::-1])  # otočení

    return list(out)

# ---------------- FETCH ----------------
def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)

        if r.status_code == 200:
            text = r.text.lower()

            if "not found" not in text:
                img = get_img(r.text)

                loc_text = extract_location(text)
                coords = None

                if loc_text:
                    coords = geocode(loc_text)
                    time.sleep(1)

                if not coords:
                    domain = url.split("/")[2]
                    coords = ip_geo(domain)

                return (url, text, img, coords, loc_text)

    except:
        pass

    return None

# ---------------- SCAN ----------------
def scan(name):
    usernames = generate(name)
    results = []

    print(Fore.YELLOW + f"\nScanning {len(usernames)} usernames...\n")

    with ThreadPoolExecutor(max_workers=40) as ex:
        futures = []

        for site, pattern in SITES:
            for u in usernames:
                futures.append(ex.submit(fetch, pattern.format(u)))

        for f in as_completed(futures):
            r = f.result()
            if r:
                print(Fore.GREEN + "[FOUND]", r[0])
                results.append(r)

    return results

# ---------------- SCORE ----------------
def score(name, url, text):
    parts = name.lower().split()
    s = 0

    if "".join(parts) in url:
        s += 50
    for p in parts:
        if p in url:
            s += 15
    if name.lower() in text:
        s += 30

    return min(s, 100)

def analyze(name, results):
    scored = [(url, score(name, url, text)) for url, text, *_ in results]
    return sorted(scored, key=lambda x: x[1], reverse=True)

# ---------------- GRAPH ----------------
def graph(name, scored, results):
    os.makedirs("graphs", exist_ok=True)

    net = Network(height="800px", width="100%", bgcolor="#111", font_color="white")
    net.add_node(name, label=name, color="red", size=35)

    map_points = []

    for url, s in scored[:40]:
        data = next((r for r in results if r[0] == url), None)
        if not data:
            continue

        _, text, img, coords, loc = data

        tooltip = f"{url}<br>Score: {s}%<br>Location: {loc if loc else 'N/A'}"

        if coords:
            map_points.append((coords[0], coords[1], url, img, loc, s))

        if img:
            net.add_node(url, shape="circularImage", image=img, size=30, title=tooltip)
        else:
            net.add_node(url, label="●", size=15, title=tooltip)

        net.add_edge(name, url)

    filename = f"graphs/{name.replace(' ', '_')}.html"
    net.write_html(filename)

    # ---------- MAP FIX ----------
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<div id="map" style="display:none;height:800px;"></div>

<div style="position:absolute;top:10px;right:10px;z-index:999;">
<button onclick="showGraph()">GRAPH</button>
<button onclick="showMap()">MAP</button>
</div>

<div style="position:absolute;bottom:10px;left:10px;background:#222;color:white;padding:10px;border-radius:10px;">
<b>Legend</b><br>
Red = Target<br>
Nodes = Profiles<br>
Hover = Info
</div>

<script>
var map;

function showGraph(){{
 document.getElementById("mynetwork").style.display="block";
 document.getElementById("map").style.display="none";
}}

function showMap(){{
 document.getElementById("mynetwork").style.display="none";
 document.getElementById("map").style.display="block";
 setTimeout(initMap,300);
}}

function initMap(){{
 if(map) return;

 map = L.map('map', {{
   center: [20,0],
   zoom: 2
 }});

 L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
   maxZoom: 19
 }}).addTo(map);

 var pts = {json.dumps(map_points)};

 pts.forEach(p => {{
   if(!p[0] || !p[1]) return;

   var marker = L.marker([p[0], p[1]]).addTo(map);

   marker.bindTooltip(
     p[2] + "<br>Score: " + p[5] + "%<br>Location: " + (p[4] || "N/A")
   );

   if(p[3]){{
     marker.bindPopup("<img src='" + p[3] + "' style='width:60px;border-radius:50%'><br>" + p[2]);
   }} else {{
     marker.bindPopup(p[2]);
   }}
 }});

 setTimeout(() => {{
   map.invalidateSize();
 }}, 500);
}}
</script>
""")

    webbrowser.open("file://" + os.path.abspath(filename))

# ---------------- MAIN ----------------
def main():
    banner()
    name = input("Enter name: ")

    results = scan(name)
    scored = analyze(name, results)

    graph(name, scored, results)

if __name__ == "__main__":
    main()