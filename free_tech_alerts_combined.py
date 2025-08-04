
import requests
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ========== SETTINGS ==========
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1401762779932790796/xBb38jH1KQr5hwlN7a3-2Z4n6-5dVToqfDwUbCRIKZ0lgqvTQs2gcRYSolTRQSFEeDwi"
SEARCH_TERMS = ["free", "0$", "no cost", "giveaway", "curb alert", "server", "rack", "switch", "router", "cpu", "gpu", "power supply", "motherboard", "network", "nas", "hdd", "ssd", "monitor", "pc", "desktop", "computer", "parts"]
CRAGSLIST_URLS = [
    "https://indianapolis.craigslist.org/search/zip",
    "https://indianapolis.craigslist.org/search/sys",
    "https://indianapolis.craigslist.org/search/ele"
]
REDDIT_SUBREDDITS = ["homelabsales", "hardwareswap", "buildapcsales", "computerdeals", "serversale"]
SEEN_POSTS = set()

# ========== FUNCTIONS ==========
def send_to_discord(title, url, source):
    message = {
        "content": f"🆕 **{title}**
From {source}
🔗 {url}"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=message)

def search_craigslist():
    for url in CRAGSLIST_URLS:
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            listings = soup.select(".result-row")
            for listing in listings:
                title = listing.select_one(".result-title").text.strip()
                link = listing.select_one("a")["href"]
                post_id = listing["data-pid"]
                if post_id in SEEN_POSTS:
                    continue
                if any(term.lower() in title.lower() for term in SEARCH_TERMS):
                    SEEN_POSTS.add(post_id)
                    send_to_discord(title, link, "Craigslist")
        except Exception as e:
            print(f"[Craigslist] Error: {e}")

def search_reddit():
    headers = {"User-Agent": "Mozilla/5.0"}
    for subreddit in REDDIT_SUBREDDITS:
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=10"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            data = res.json()
            for post in data.get("data", {}).get("children", []):
                post_data = post["data"]
                post_id = post_data["id"]
                title = post_data["title"].lower()
                if post_id in SEEN_POSTS:
                    continue
                if any(term in title for term in SEARCH_TERMS):
                    SEEN_POSTS.add(post_id)
                    send_to_discord(post_data["title"], f"https://reddit.com{post_data['permalink']}", f"r/{subreddit}")
        except Exception as e:
            print(f"[Reddit] Error scraping r/{subreddit}: {e}")

# ========== MAIN LOOP ==========
if __name__ == "__main__":
    print("📡 Starting Tech Scraper Alerts")
    while True:
        print(f"🔄 Checking sources at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        search_craigslist()
        search_reddit()
        time.sleep(900)  # Run every 15 minutes
