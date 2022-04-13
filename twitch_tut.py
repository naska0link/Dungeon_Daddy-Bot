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
import requests
from twitchAPI.twitch import Twitch

from irc.bot import SingleServerIRCBot
from requests import get
from collections import defaultdict
from getoauth import refresh_token, getoauth_token
from commands import db, cmds, react, polls
from threading import Timer

# pip install python-dotenv
from dotenv import load_dotenv


# The Twitch Bot
class Bot(SingleServerIRCBot):
    def __init__(
        self,
        BOT_NAME,
        CLIENT_ID,
        TOKEN,
        CHANNELS,
        DISCORD_WEBHOOK,
        SECRET,
        DM=False,
        PORT=6667,
        HOST="irc.chat.twitch.tv",
    ):
        # Setting bot self variable
        self.BOT_NAME = BOT_NAME.lower()
        self.CLIENT_ID = CLIENT_ID
        self.SECRET = SECRET
        self.TOKEN = TOKEN
        self.CHANNELS = CHANNELS.split(",")
        self.DM = []
        self.PORT = PORT
        self.HOST = HOST
        self.CHANNEL_IDS = defaultdict()
        self.sub_list = defaultdict()
        self.update_access_token()
        self.poll = polls.Poll()
        self.PREFIX = "!"
        self.DISCORD_WEBHOOK = DISCORD_WEBHOOK

        # Connection points for bot
        self.twitch = Twitch(self.CLIENT_ID, self.SECRET)

        # url = f"https://api.twitch.tv/kraken/users?login={self.BOT_NAME}"
        # headers = {
        #     "Client-ID": self.CLIENT_ID,
        #     "Accept": "application/vnd.twitchtv.v5+json",
        # }
        # Goes through each channel and obtain subscriber list and channel ids
        for channel_name in self.CHANNELS:
            channel_id = self.twitch.get_users(logins=[channel_name[1:]])
            channel_id = channel_id["data"][0]["id"]
            if channel_name in DM:
                self.DM.append(channel_id)
            self.CHANNEL_IDS[channel_name] = channel_id
        self.CHANNEL_IDS_LIST = [int(self.CHANNEL_IDS[key]) for key in self.CHANNEL_IDS]
        # Connects the bot to Twitch and allows it to chat and stuff
        resp = self.twitch.get_users(logins=[self.BOT_NAME])
        self.channel_id = resp["data"][0]["id"]
        super().__init__(
            [(self.HOST, self.PORT, self.TOKEN)], self.BOT_NAME, self.BOT_NAME
        )

    # Updates the sub list
    def update_sub_list(self):
        for channel_name, channel_id in self.CHANNEL_IDS.items():
            self.sub_list[channel_name] = self.get_sublist(
                channel_id, self.CLIENT_ID, self.ACCESS_TOKEN[channel_name]
            )
        self.update_sub_list_timer = Timer(60, self.update_sub_list)
        self.update_sub_list_timer.start()

    # Updates the access token every hour
    def update_access_token(self):
        print("Updated Access Token")
        self.ACCESS_TOKEN = refresh_token()
        self.update_access_token_timer = Timer(3600, self.update_access_token)
        self.update_access_token_timer.start()

    def _resend_copyright(self):
        self.send_message_all(
            "Twitchpaign is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC."
        )
        self._resend_copyright = Timer(1800, self._resend_copyright)
        self._resend_copyright.start()

    # Runs when the bot connects to the channels
    def on_welcome(self, cxn, event):
        # Updates the subscription list
        self.update_sub_list()
        # Connects to the channels
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")
        # Sends to each channel a message saying it is online
        for channel in self.CHANNELS:
            print(f"Joined: {channel}")
            cxn.join(channel)
            self.send_message("Now online.", channel)
        self.discord_log({"content": "Now online."})
        self._resend_copyright()
        # Builds the database, and makes sure the that they are set up right
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
        print("\n")

    # Everytime a message is sent in chat
    @db.with_commit
    def on_pubmsg(self, cxn, event):
        # Process the event
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {
            "name": tags["display-name"],
            "id": tags["user-id"],
            "msgid": tags["id"],
        }
        message = event.arguments[0]
        channel = event.target
        # Makes sure that the message is not the bots, then proccess the message
        if user["name"] != self.BOT_NAME:
            react.process(self, user, message, channel)
            cmds.process(self, user, message, channel)
            self.poll = polls.process(self, user, message, channel, self.poll)

        print(f"Message from {user['name']} in {channel}: {message}")

    # Allows the bot to send message to the channels
    def send_message(self, message, channel):
        self.connection.privmsg(channel, message)

    def send_message_all(self, message):
        for channel in self.CHANNELS:
            self.connection.privmsg(channel, message)

    def get_sublist(self, channel_id, client_id, access_token):
        response = get(
            f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}",
            headers={"Client-ID": client_id, "Authorization": f"Bearer {access_token}"},
        )
        result = response.json()
        try:
            if result["error"]:
                return "error"
        except:
            sub_list = []
            for sub in result["data"]:
                sub_list.append((int(sub["user_id"]), int(sub["tier"])))
            return np.array(sub_list)

    def discord_log(self, message):
        requests.post(
            self.DISCORD_WEBHOOK,
            message,
        )


# Builds the twitch bot
def make_twitch_bot(
    bot_name, client_id, token, streamer, DISCORD_WEBHOOK, SECRET, DM=False
):
    bot = Bot(bot_name, client_id, token, streamer, DISCORD_WEBHOOK, SECRET, DM=DM)
    bot.start()
    return bot


if __name__ == "__main__":
    load_dotenv()
    twitch_bot = make_twitch_bot(
        os.getenv("BOT_NAME"),
        os.getenv("CLIENT_ID"),
        os.getenv("TOKEN"),
        os.getenv("STREAMERS"),
        os.getenv("DISCORD_WEBHOOK"),
        os.getenv("SECRET"),
        DM=os.getenv("DM").split(","),
    )
