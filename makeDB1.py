import requests
import pandas
from pandas import json_normalize
import numpy
import json
import time
import sys
import IDsandboxXtwitch
import namesandboxXtwitch

sys.setrecursionlimit(7000)

IDsandboxXtwitch_list = IDsandboxXtwitch.IDsandboxXtwitch[0:26]
namesandboxXtwitch_list = namesandboxXtwitch.namesandboxXtwitch[0:26]

hdr = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Authorization": "Bearer jrozxlf42pe3nbmegn1wvk5g8g9fli",
    "Client-Id": "2zy5ild6yrrvzaopivonrwgj9ets51",
}

df_streamers = pandas.DataFrame(
    [],
    columns=[
        "broadcaster_language",
        "broadcaster_login",
        "display_name",
        "game_id",
        "game_name",
        "id",
        "is_live",
        "tag_ids",
        "thumbnail_url",
        "title",
        "started_at",
        "follows_count",
    ],
)

df_follows = pandas.DataFrame(
    [],
    columns=[
        "from_id",
        "from_login",
        "from_name",
        "to_id",
        "to_login",
        "to_name",
        "followed_at",
    ],
)


def getfollows(to_id, cursor):
    global df_follows
    payload = {"to_id": numberid, "first": 100, "after": cursor}
    url = "https://api.twitch.tv/helix/users/follows"
    response = requests.get(url, params=payload, headers=hdr)
    print("*", end="")
    if response.status_code == 200:
        info = response.json()
        df = json_normalize(info["data"])
        df_follows = pandas.concat([df_follows, df])
        cursor = info["pagination"]
        if cursor:
            getfollows(to_id, cursor["cursor"])


for name in IDsandboxXtwitch_list:
    print(".", end="")
    payload = {"query": name}
    url = "https://api.twitch.tv/helix/search/channels"
    response = requests.get(url, params=payload, headers=hdr)
    if response.status_code == 200:
        info = response.json()
        df = json_normalize(info["data"])
        df = df.loc[df.display_name == name]
        df_streamers = pandas.concat([df_streamers, df])
df_streamers.set_index("id", inplace=True)
print(".")

for numberid in IDsandboxXtwitch_list:
    payload = {"to_id": numberid, "first": 100}
    url = "https://api.twitch.tv/helix/users/follows"
    response = requests.get(url, params=payload, headers=hdr)
    if response.status_code == 200:
        info = response.json()
        df_streamers.loc[str(numberid), "follows_count"] = info["total"]
        df = json_normalize(info["data"])
        df_follows = pandas.concat([df_follows, df])
        cursor = info["pagination"]["cursor"]
        getfollows(numberid, cursor)
        print(str(numberid) + "-done")

df_streamers.to_csv("df_streamers1.csv")
df_follows.to_csv("df_follows1.csv")
