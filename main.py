import csv
from itertools import product
import os
from bson import ObjectId
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
fake.unique.clear()

NUM_USERS = 20_000
NUM_ARTICLES = 20_000
NUM_EVENTS = 20_000

USERS_CSV = "data/users.csv"
EVENTS_CSV = "data/events.csv"
ARTICLES_JSON = "data/articles.json"
DEVICES_CSV = "data/devices.csv"

# "123456"
USER_PASSWORD = "$2b$12$KnWOu/UPlzpcU6vxfElpg.wwsg3krvXFBLeloxUdKu7F0rk0UbFLW"

os.makedirs("data", exist_ok=True)

print("Generating users...")

users = []
for _ in range(NUM_USERS):
    user = {
        "id": fake.uuid4(),
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password_hash": USER_PASSWORD,
        "inserted_at": fake.date_time_between(start_date="-2y", end_date="-1y"),
        "updated_at": fake.date_time_between(start_date="-1y", end_date="now"),
    }
    users.append(user)

with open(USERS_CSV, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=users[0].keys())
    writer.writeheader()
    writer.writerows(users)

print(f"Wrote {len(users)} users to {USERS_CSV}")

print("Generating articles...")

articles = []

for _ in range(NUM_ARTICLES):
    author = random.choice(users)
    article = {
        "_id": str(ObjectId()),
        "title": fake.sentence(nb_words=6),
        "author_id": author["id"],
        "tags": [fake.word() for _ in range(random.randint(1, 5))],
        "content": fake.paragraph(nb_sentences=5),
        "commentsCount": random.randint(0, 50),
        "createdAt": fake.date_time_between(start_date="-2y", end_date="-1y").isoformat(),
        "updatedAt": fake.date_time_between(start_date="-1y", end_date="now").isoformat()
    }
    articles.append(article)

with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(articles)} articles to {ARTICLES_JSON}")

print("Generating devices...")

# Define some realistic values
oses = ["Windows", "macOS", "Linux", "Android", "iOS"]
browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
resolutions = ["1920x1080", "1366x768", "1440x900", "2560x1440", "1280x720"]
languages = ["en", "es", "fr", "de", "zh"]

# Create all unique combinations
all_device_combinations = list(product(oses, browsers, resolutions, languages))
random.shuffle(all_device_combinations)  # shuffle to pick randomly

devices = []
device_map = {}  # maps (os, browser, res, lang) -> device id

for i, (os_, browser, res, lang) in enumerate(all_device_combinations):
    device = {
        "id": i + 1,
        "os": os_,
        "browser": browser,
        "screen_resolution": res,
        "language": lang
    }
    devices.append(device)
    device_map[(os_, browser, res, lang)] = device["id"]

with open(DEVICES_CSV, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=devices[0].keys())
    writer.writeheader()
    writer.writerows(devices)

print(f"Wrote {len(devices)} devices to {DEVICES_CSV}")

print("Generating events...")

events = []
event_kinds = ["view", "like", "share"]

for _ in range(NUM_EVENTS):
    user = random.choice(users)
    article = random.choice(articles)
        # Most events have a device
    if random.random() < 0.9:  # 90% chance
        os_ = random.choice(oses)
        browser = random.choice(browsers)
        res = random.choice(resolutions)
        lang = random.choice(languages)
        device_id = device_map[(os_, browser, res, lang)]
    else:
        device_id = None

    event = {
        "id": _ + 1,
        "user_id": user["id"],
        "post_id": article["_id"],
        "kind": random.choice(event_kinds),
        "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S"),
        "device_id": device_id
    }
    events.append(event)

with open(EVENTS_CSV, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=events[0].keys())
    writer.writeheader()
    writer.writerows(events)

print(f"Wrote {len(events)} events to {EVENTS_CSV}")

