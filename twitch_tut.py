"""
	COPYRIGHT INFORMATION
	---------------------
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
	NOTES
	-----
"""
import os

from irc.bot import SingleServerIRCBot
from requests import get

# pip install python-dotenv
from dotenv import load_dotenv


class Bot(SingleServerIRCBot):
    def __init__(self,
                 USERNAME,
                 CLIENT_ID,
                 TOKEN,
                 CHANNEL,
                 DM=False,
                 PORT=6667,
                 HOST="irc.chat.twitch.tv"):

        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.IS_DM = DM
        self.USERNAME = USERNAME
        self.CLIENT_ID = CLIENT_ID
        self.TOKEN = TOKEN
        self.CHANNEL = f"#{CHANNEL}"

        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json"
        }
        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]
        super().__init__([(self.HOST, self.PORT, f"{self.TOKEN}")],
                         self.USERNAME, self.USERNAME)

    def on_welcome(self, cxn, event):
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")

        cxn.join(self.CHANNEL)
        self.send_message("Now online.")

    def on_pubmsg(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags['display-name'], "id": tags['user-id']}
        message = event.arguments[0]

        print(f"Message from {user['name']} in {self.CHANNEL[1:]}: {message}")

    def send_message(self, message):
        self.connection.privmsg(self.CHANNEL, message)


if __name__ == '__main__':
    # with open('.env') as f:

    load_dotenv()

    streamers_bots = {
        streamer: Bot(os.getenv('BOT_NAME').lower(),
                      os.getenv('CLIENT_ID'),
                      os.getenv(f'{streamer}_TOKEN'),
                      streamer,
                      DM=(streamer == os.getenv('DM')))
        for streamer in os.getenv('STEAMER_LIST').split(',')
    }

    # naska_link_bot = Bot(
    #     os.getenv('BOT_NAME').lower(), os.getenv('CLIENT_ID'),
    #     os.getenv('TOKEN'), os.getenv('OWNER'))
    # naska_link_bot.start()

    [bot.start() for bot in streamers_bots.values()]
