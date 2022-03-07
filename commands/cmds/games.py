from random import choice, randint
from time import time

from .. import db

heist = None
heist_lock = time()


def coinflip(bot, user, channel, side=None, *args):
    if side is None:
        bot.send_message("You need to guess which side the coin will land!",
                         channel)
    elif (side := side.lower()) not in (opt := ('h', 't', 'heads', 'tails')):
        bot.send_message(
            "Enter one of the following as the side: " + ", ".join(opt),
            channel)
    else:
        result = choice(("heads", "tails"))

        if side[0] == result[0]:
            db.execute("UPDATE users SET Coins = Coins + 50 WHERE UserID = ?",
                       user['id'])
            bot.send_message(f"It Landed on {result}: You won 50 coins!",
                             channel)
        else:
            bot.send_message(
                f"Too bad - it landed on {result}. You didn't win anything!",
                channel)


class Heist(object):
    def __init__(self):
        self.users = []
        self.running = False
        self.start_time = time() + 60
        self.end_time = 0
        self.messages = {
            "success": [
                "{} fought off the guards, and got their haul!",
                "{} sneaked out of the back entrance with their share!",
                "{} got in and out seemlessly with their money!",
            ],
            "fail": [
                "{} got caught by the guards!",
                "{} was injured by a gunshot!",
                "{} got lost!",
            ]
        }

    def add_user(self, bot, user, bet, channel):
        if self.running:
            bot.send_message(
                "A heist is already in progress. You'll have to wait until the next one.",
                channel)
        elif user in self.users:
            bot.send_message("You're already good to go.", channel)

        elif bet > (coin := db.field(
                "SELECT Coins FROM users WHERE UserID = ?", user['id'])):
            bot.send_message(
                f"You don't have that much to bet - you only have {coin:,} coins.",
                channel)
        else:
            db.execute("UPDATE users SET Coins = Coins - ? WHERE UserID = ?",
                       bet, user['id'])
            self.users.append((user, bet))
            bot.send_message(
                "You're all suited and ready to go! Stand by for showtime...",
                channel)

    def start(self, bot, channel):
        bot.send_message("The heist has started! Standby for results...",
                         channel)
        self.running = True
        self.end_time = time() + randint(30, 60)

    def end(self, bot, channel):
        succeeded = []

        for user, bet in self.users:
            if randint(0, 1):
                db.excute(
                    "UPDATE users SET Coins = Coins + ? WHERE UserID = ?",
                    bet * 1.5, user['id'])
                succeeded.append((user, bet * 1.5))
                bot.send_message(
                    choice(self.messages['success']).format(user["name"]),
                    channel)
            else:
                bot.send_message(
                    choice(self.messages['fail']).format(user["name"]),
                    channel)
        if len(succeeded) > 0:
            bot.send_message("The heist is over! The winners: " + ", ".join([
                f"{user['name']} ({coins:,} coins)"
                for user, coins, coins in succeeded
            ]))
        else:
            bot.send_message("The heist was a failure! No one got out!")


def start_heist(bot, user, channel, bet=None, *args):
    global heist

    if bet is None:
        bot.send_message("You need to specify an amount to bet.", channel)

    else:
        try:
            bet = int(bet)

        except ValueError:
            bot.send_message("That's not a valid bet.", channel)
        else:
            if bet < 1:
                bot.send_message("You need to bet at least 1 coin.", channel)

            else:
                if bet < 1:
                    bot.send_message("You need to bet at least 1 coin.",
                                     channel)

                else:
                    if heist is None:
                        heist = Heist()

                    heist.add_user(bot, user, bet, channel)


def run_heist(bot, channel):
    heist.start(bot, channel)


def end_heist(bot, channel):
    global heist

    heist.end(bot, channel)
    heist = None
