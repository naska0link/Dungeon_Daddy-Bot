"""
	COPYRIGHT INFORMATION
	---------------------
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
	NOTES
	-----
"""
# import statements
import os
import numpy as np

from irc.bot import SingleServerIRCBot
from requests import get
from collections import defaultdict
from getoauth import refresh_token, getoauth_token
from lib import db, cmds, react, polls
from threading import Timer

# pip install python-dotenv
from dotenv import load_dotenv


# The Twitch Bot
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
        self.DM = []
        self.PORT = 6667
        self.HOST = HOST
        self.CHANNEL_IDS = defaultdict()
        self.sub_list = defaultdict()
        self.update_access_token()
        self.poll = polls.Poll()
        self.PREFIX = '!'

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
            if channel_name in DM:
                self.DM.append(channel_id)
            self.CHANNEL_IDS[channel_name] = channel_id
            print(channel_name, channel_id)
            self.sub_list[channel_name] = get_sublist(
                channel_id, self.CLIENT_ID, self.ACCESS_TOKEN[channel_name])
        self.CHANNEL_IDS_LIST = [
            int(self.CHANNEL_IDS[key]) for key in self.CHANNEL_IDS
        ]

        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]
        super().__init__([(self.HOST, self.PORT, self.TOKEN)], self.BOT_NAME,
                         self.BOT_NAME)

    def update_access_token(self):
        print('Updated Access Token')
        self.ACCESS_TOKEN = refresh_token()
        t = Timer(3600, self.update_access_token)
        t.start()

    def on_welcome(self, cxn, event):
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")
        for channel in self.CHANNELS:
            print(f'Joined: {channel}')
            cxn.join(channel)
            self.send_message("Now online.", channel)

        db.build()
        for channel in self.CHANNELS:
            try:
                db.execute(
                    f"ALTER TABLE coincooldowns ADD COLUMN {channel[1:]} text DEFAULT CURRENT_TIMESTAMP;"
                )
            except:
                pass
            try:
                db.execute(
                    f"ALTER TABLE gemcooldowns ADD COLUMN {channel[1:]} text DEFAULT CURRENT_TIMESTAMP;"
                )
            except:
                pass
        print('\n')

    @db.with_commit
    def on_pubmsg(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {
            "name": tags['display-name'],
            "id": tags['user-id'],
            "msgid": tags['id']
        }
        message = event.arguments[0]
        channel = event.target
        if user["name"] != self.BOT_NAME:
            react.process(self, user, message, channel)
            cmds.process(self, user, message, channel)
            self.poll = polls.process(self, user, message, channel, self.poll)

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
            sub_list.append((int(sub['user_id']), int(sub['tier'])))
        return np.array(sub_list)


if __name__ == '__main__':
    load_dotenv()
    twitch_bot = make_twitch_bot(os.getenv('BOT_NAME'),
                                 os.getenv('CLIENT_ID'),
                                 os.getenv('TOKEN'),
                                 os.getenv('STREAMERS'),
                                 DM=os.getenv('DM').split(','))
