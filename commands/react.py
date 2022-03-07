from datetime import datetime, timedelta
from collections import defaultdict
from random import randint
from re import search
from time import time

from . import db
from .cmds import games

welcomed = []
messages = defaultdict(int)


def process(bot, user, message, channel):
    update_records(bot, user, channel)

    if (match := search(r"cheer[0-9]+", message)) is not None:
        thank_for_cheer(bot, user, match, channel)


def update_records(bot, user, channel):
    db.execute("INSERT OR IGNORE INTO userbalance (UserID) VALUES (?)", user["id"])
    db.execute("INSERT OR IGNORE INTO coincooldowns (UserID) VALUES (?)", user["id"])
    db.execute("INSERT OR IGNORE INTO gemcooldowns (UserID) VALUES (?)", user["id"])
    db.execute(
        "UPDATE userbalance SET MessagesSent = MessagesSent + 1 WHERE UserID = ?",
        user["id"],
    )

    userid = int(user["id"])
    sublist = bot.sub_list[channel]
    subluck = 1
    if type(sublist) != str:
        subscribed = sublist[sublist[:, 0] == userid, 1]
        subluck = (
            int(2 ** (0 if subscribed < 1000 else subscribed / 1000))
            if len(subscribed) > 0
            else 1
        )

    c_stamp = db.field(
        f"SELECT {channel[1:]} FROM coincooldowns WHERE UserID = ?", user["id"]
    )
    if datetime.strptime(c_stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
        coinlock = (datetime.utcnow() + timedelta(seconds=60)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        db.execute(
            f"UPDATE userbalance SET Coins = Coins + ? WHERE UserID = ?",
            randint(1 * subluck, 5 * subluck),
            user["id"],
        )
        db.execute(
            f"UPDATE coincooldowns SET {channel[1:]} = ? WHERE UserID = ?",
            coinlock,
            user["id"],
        )

    g_stamp = db.field(
        f"SELECT {channel[1:]} FROM gemcooldowns WHERE UserID = ?", user["id"]
    )
    if (
        datetime.strptime(g_stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow()
        and subluck > 1
    ):
        coinlock = (datetime.utcnow() + timedelta(seconds=300)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        db.execute(
            f"UPDATE userbalance SET Gems = Gems + ? WHERE UserID = ?",
            randint(1, 5) + subluck,
            user["id"],
        )
        db.execute(
            f"UPDATE gemcooldowns SET {channel[1:]} = ? WHERE UserID = ?",
            coinlock,
            user["id"],
        )


# def welcome(bot, user, channel):
#     bot.send_message(f"Welcome to the stream {user['name']}", channel)
#     welcomed.append(user["id"])

# def say_goodbye(bot, user, channel):
#     bot.send_message(f"See ya later {user['name']}!", channel)

# def check_activity(bot, user, channel):
#     messages[user["id"]] += 1

#     if (count := messages[user["id"]]) % 3 == 0:
#         bot.send_message(
#             f"Thanks for being active in chat {user['name']} = you've sent {count:,} messages! Keep it up!!!",
#             channel)


def thank_for_cheer(bot, user, match, channel):
    bot.send_message(
        f"Thanks for the {match.match[5:]:,} bits {user['name']}! That's really appreciated!",
        channel,
    )
    db.execute(
        f"UPDATE userbalance SET Gems = Gems + ? WHERE UserID = ?",
        int(match.match[5:]),
        user["id"],
    )
