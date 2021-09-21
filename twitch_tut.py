"""
	COPYRIGHT INFORMATION
	---------------------
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
	NOTES
	-----
"""
import os
import numpy as np

from irc.bot import SingleServerIRCBot
from requests import get
from collections import defaultdict
from getoauth import refresh_token, getoauth_token
from lib import db, cmds, react

# pip install python-dotenv
from dotenv import load_dotenv


class Bot(SingleServerIRCBot):
    def __init__(self,
                 BOT_NAME,
                 CLIENT_ID,
                 TOKEN,
                 CHANNELS,
                 DM=False,
                 PORT=6667,
                 HOST="irc.chat.twitch.tv"):

        self.BOT_NAME = BOT_NAME.lower()
        self.CLIENT_ID = CLIENT_ID
        self.TOKEN = TOKEN
        self.CHANNELS = CHANNELS.split(',')
        self.IS_DM = DM
        self.PORT = 6667
        self.HOST = HOST
        self.ACCESS_TOKEN = refresh_token()
        self.CHANNEL_IDS = defaultdict()
        self.sub_list = defaultdict()

        url = f"https://api.twitch.tv/kraken/users?login={self.BOT_NAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json"
        }
        for channel_name in self.CHANNELS:
            channel_id = get(
                f"https://api.twitch.tv/kraken/users?login={channel_name[1:]}",
                headers=headers).json()
            channel_id = channel_id["users"][0]["_id"]
            self.CHANNEL_IDS[channel_name] = channel_id
            print(channel_name, channel_id)
            self.sub_list[channel_name] = get_sublist(
                channel_id, self.CLIENT_ID, self.ACCESS_TOKEN[channel_name])
        print(self.sub_list)
        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]
        super().__init__([(self.HOST, self.PORT, self.TOKEN)], self.BOT_NAME,
                         self.BOT_NAME)

    def on_welcome(self, cxn, event):
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")
        for channel in self.CHANNELS:
            print(f'Joined: {channel}')
            cxn.join(channel)
            self.send_message("Now online.", channel)
        db.build()
        print('\n')

    @db.with_commit
    def on_pubmsg(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags['display-name'], "id": tags['user-id']}
        message = event.arguments[0]
        channel = event.target
        if user["name"] != self.BOT_NAME:
            react.process(self, user, message, channel)
            cmds.process(self, user, message, channel)

        print(f"Message from {user['name']} in {channel}: {message}")

    def send_message(self, message, channel):
        self.connection.privmsg(channel, message)


def make_twitch_bot(bot_name, client_id, token, streamer, DM=False):
    bot = Bot(bot_name, client_id, token, streamer, DM=DM)
    bot.start()
    return bot


def get_sublist(channel_id, client_id, access_token):
    response = get(
        f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}",
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        })
    result = response.json()
    try:
        if result['error']:
            return "error"
    except:
        sub_list = []
        for sub in result['data']:
            if (sub_id := sub['user_id']) != channel_id:
                print(sub_id)
                sub_list.append((int(sub_id), int(sub['tier'])))
        return np.array(sub_list)


if __name__ == '__main__':
    load_dotenv()
    twitch_bot = make_twitch_bot(os.getenv('BOT_NAME'),
                                 os.getenv('CLIENT_ID'),
                                 os.getenv('TOKEN'),
                                 os.getenv('STREAMERS'),
                                 DM=os.getenv('DM').split(','))
