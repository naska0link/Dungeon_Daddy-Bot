from . import db
from collections import defaultdict
from time import time
from threading import Timer
import shlex
import random


class Poll(object):
    def __init__(self):
        self.user_votes = {}
        self.running = False
        self.start_time = time() + 60
        self.end_time = 0

    def caste_vote(self, bot, user, channel, vote):
        self.user_votes[channel][user["id"]] = vote
        self.repeat_options()

    def start_vote(self, bot, vote_len, query, options):
        # print("Starting vote")
        self.user_votes = {channel: defaultdict() for channel in bot.CHANNELS}
        option_str = ", ".join([f'{op} for "{cho}"' for op, cho in options.items()])
        self.query = query
        self.options = options
        self.option_str = option_str
        self.bot = bot
        self.bot.send_message_all(f"A vote has been started: [{query}] {option_str}.")
        self.vote_casted_count = 0
        self.bot.discord_log(
            {"content": f"A vote has been started: [{query}] {option_str}."}
        )
        vote_len = int(vote_len[:-1]) * (
            60 if vote_len[-1] == "m" else 1 if vote_len[-1] == "s" else 1
        )
        self.end_vote_timer = Timer(vote_len, self.end_vote)
        self.end_vote_timer.start()
        self.repeat_options_timer = Timer(30, self.repeat_options)
        self.repeat_options_timer.start()
        self.running = True

    def print_options(self, user, channel):
        self.bot.send_message(
            f"{user['name']} the vote is for [{self.query}] {self.option_str}.", channel
        )

    def repeat_options(self):
        self.vote_casted_count += 1
        if self.vote_casted_count % 100 == 0:
            self.bot.send_message_all(
                f"There is an ongoing vote for [{self.query}] {self.option_str}.",
            )

    def stop_vote(self):
        self.running = False
        self.end_vote_timer.cancel()
        self.repeat_options_timer.cancel()
        for chan in self.bot.CHANNELS:
            self.bot.send_message(f"The vote has been manually stopped.", chan)

    def end_vote(self):
        # print('voting has ended')
        if self.running:
            self.running = False
            self.vote_count = {}
            votes = []
            self.end_vote_timer.cancel()
            self.repeat_options_timer.cancel()
            for channel_votes in self.user_votes:
                for user_vote in self.user_votes[channel_votes].values():
                    votes += user_vote
            for opt in self.options:
                self.vote_count[opt] = votes.count(opt)
            winning_vote = max(self.vote_count, key=self.vote_count.get)
            winning_vote_lst = [
                key
                for key, val in self.vote_count.items()
                if val == self.vote_count[winning_vote]
            ]
            if self.vote_count[winning_vote] == 0:
                option, choice = random.choice(list(self.options.items()))
                self.bot.send_message_all(
                    f"There where no votes casted, so picking a random one: Option {option} for {choice} has been picked."
                )
                self.bot.discord_log(
                    {
                        "content": f"There where no votes casted, so picking a random one: Option {option} for {choice} has been picked."
                    }
                )
            elif len(winning_vote_lst) > 1:
                win_vote = random.choice(winning_vote_lst)
                self.bot.send_message_all(
                    f"There where was a tie, so picking a random one: Option {self.options[win_vote]} for {self.vote_count[win_vote]} has been picked."
                )
                self.bot.discord_log(
                    {
                        "content": f"There where was a tie, so picking a random one: Option {self.options[win_vote]} for {self.vote_count[win_vote]} has been picked."
                    }
                )

            else:
                self.bot.send_message_all(
                    f"The vote has ended, {self.options[winning_vote]} has won with {self.vote_count[winning_vote]} votes."
                )
                self.bot.discord_log(
                    {
                        "content": f"The vote has ended, {self.options[winning_vote]} has won with {self.vote_count[winning_vote]} votes."
                    }
                )


def process(bot, user, message, channel, poll):
    if poll.running:
        sublist = bot.sub_list[channel]
        subluck = 1
        if type(sublist) != str:
            subscribed = sublist[sublist[:, 0] == int(user["id"]), 1]
            subluck = (
                int(2 ** (0 if subscribed < 1000 else subscribed / 1000))
                if len(subscribed) > 0
                else 1
            )
        if message in poll.options.keys():
            poll.caste_vote(bot, user, channel, [message] * subluck)
        elif message.lower() in poll.options.values():
            poll.caste_vote(
                bot,
                user,
                channel,
                [
                    list(poll.options.keys())[
                        list(poll.options.values()).index(message.lower())
                    ]
                ]
                * subluck,
            )
        if message.startswith(bot.PREFIX):
            if message.split(" ")[0][len(bot.PREFIX) :] in [
                "vote",
                "options",
                "question",
            ]:
                poll.print_options(user, channel)
            if user["id"] in bot.DM:
                if message.split(" ")[0][len(bot.PREFIX) :] in [
                    "stop_vote",
                    "stop_poll",
                ]:
                    poll.stop_vote()
                elif message.split(" ")[0][len(bot.PREFIX) :] in [
                    "end_vote",
                    "end_poll",
                ]:
                    poll.end_vote()
    elif user["id"] in bot.DM:
        # print("User is DM")
        if message.startswith(bot.PREFIX):
            # print('message start with bot prefix')
            if (msg_splt := shlex.split(message))[0][len(bot.PREFIX) :] == "start_vote":
                options = {
                    str(ind + 1): opt.lower() for ind, opt in enumerate(msg_splt[3:])
                }
                poll.start_vote(bot, msg_splt[1], msg_splt[2], options)
    else:
        pass
    return poll
