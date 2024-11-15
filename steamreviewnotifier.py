import os
import time
import requests
from discord import Embed, SyncWebhook
from datetime import datetime, timezone

#* Discord webhook URL
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

#* Steam app id
STEAM_APP_ID = os.getenv('STEAM_APP_ID')

#* Steam API Key
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

#* File to store the last review timestamp or ID
TIMESTAMP_FILE = os.getenv("TIMESTAMP_FILE", 'timestamp.txt')

def get_steam_user(steam_user_id, api_key):
    if not api_key:
        return steam_user_id
    
    #* Steam API endpoint for GetPlayerSummaries
    url = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_user_id}'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'players' in data['response']:
            player_data = data['response']['players'][0]
            #* Return the player's Steam name
            return player_data.get('personaname', steam_user_id)
        else:
            return steam_user_id
    else:
        return f"Error: {response.status_code}"

def load_last_timestamp():
    try:
        with open(TIMESTAMP_FILE, 'r') as f:
            s = f.read()
            print(f'Loaded timestamp {s}')
            return datetime.fromtimestamp(int(s), timezone.utc)
    except FileNotFoundError:
        #return datetime.fromtimestamp(0, timezone.utc) #* Epoch for testing
        return datetime.now(timezone.utc)

def save_last_timestamp(ts_object):
    with open(TIMESTAMP_FILE, 'w') as f:
        s = str(int(ts_object.timestamp()))
        f.write(s)
        print(f'Saved timestamp {s}')

def truncate_string(s, max_length):
    return s[:max_length] if len(s) > max_length else s

def str_to_bool(s):
    return str(s).lower() in ['true', '1', 'y', 't']

def send_discord_notification(webhook, title, message, timeObj, url):
    print(f'{title}\n{message}')
    embed = Embed(title=truncate_string(title,256), description=truncate_string(message,4096), timestamp=timeObj, color=0x171a21, url=url)
    webhook.send(embed=embed, username="Steam Reviews", avatar_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/1024px-Steam_icon_logo.svg.png")

def check_new_reviews():
    #* Fetch reviews data from Steam
    steam_url = f'https://store.steampowered.com/appreviews/{STEAM_APP_ID}?purchase_type=all&json=1'
    response = requests.get(steam_url)
    if response.status_code != 200:
        raise Exception(f'Failed to retrieve APP URL {steam_url}\nStatus code {response.status_code}.')

    reviews_data = response.json()
    reviews = reviews_data.get('reviews', [])

    webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)

    if not reviews:
        print("No reviews found")
        return

    #* Load the last timestamp
    last_timestamp = load_last_timestamp()
    most_recent_timestamp = last_timestamp

    #* Poll the reviews
    print(f'Checking for new reviews...')
    new_reviews = 0
    for review in reviews:
        review_timestamp = datetime.fromtimestamp(review['timestamp_created'], timezone.utc)

        #* Only notify for reviews newer than our saved timestamp
        if (review_timestamp <= last_timestamp):
            continue

        #* most_recent_timestamp keeps track of the latest timestamp in this poll
        if (review_timestamp > most_recent_timestamp):
            most_recent_timestamp = review_timestamp

        new_reviews += 1

        #* Parse info
        review_text = review.get('review', 'No review text available.')
        review_steam_id = review.get('author', {}).get('steamid', 'Unknown')
        review_author = get_steam_user(review_steam_id, STEAM_API_KEY)
        review_rating = "Positive" if str_to_bool(review.get('voted_up')) else "Negative"
        review_link = f'https://steamcommunity.com/profiles/{review_steam_id}/recommended/{STEAM_APP_ID}/'

        #* Send the Discord notification
        title = f"New {review_rating} Review Posted by {review_author}"
        message = f"{review_text}"
        send_discord_notification(webhook, title, message, review_timestamp, review_link)

    if new_reviews > 0:
        print(f'Found {new_reviews} new reviews.')
    else:
        print(f'No new reviews found.')

    #* Save the most recent review timestamp, any review posted after this one will be polled next time
    last_timestamp = most_recent_timestamp
    save_last_timestamp(last_timestamp)

if not STEAM_API_KEY:
    print("WARNING: No Steam API Key configured, usernames will not be shown in Discord Notifications.")

if not STEAM_APP_ID:
    raise Exception("STEAM_APP_ID required")

if not DISCORD_WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK_URL required")

while True:
    check_new_reviews()
    time.sleep(60)