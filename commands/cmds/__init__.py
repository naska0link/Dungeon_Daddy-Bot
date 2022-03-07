from time import time
from . import misc, economy, cmd
import shlex
from .. import db

PREFIX = "!"


class Cmd(object):
    def __init__(self, callables, func, cooldown=0):
        self.callables = callables
        self.func = func
        self.cooldown = cooldown
        self.next_use = time()


# cmds = {"hello": misc.hello}

cmds = [
    #   economy
    Cmd(["bal", "balance"], economy.balance, cooldown=1),
    #   Games
    Cmd(["copyright"], misc.copyright),
    # Shop
    Cmd(["buy", "purchase"], economy.purchase, cooldown=1),
    Cmd(["shop", "store"], economy.display_shop, cooldown=1),
]

hidden_cmds = [
    # shop
    Cmd(["add_item"], economy.add_shop),
    Cmd(["edit_item"], economy.edit_shop),
    Cmd(["remove_item"], economy.remove_shop),
    Cmd(["add_cmd"], cmd.add_command),
    Cmd(["edit_cmd"], cmd.edit_command),
    Cmd(["rm_cmd"], cmd.remove_command),
]

all_cmds = cmds + hidden_cmds


def process(bot, user, message, channel):
    if message.startswith(bot.PREFIX):
        cmd = message.split(" ")[0][len(bot.PREFIX) :]
        args = shlex.split(message)[1:]
        react_cmd = db.field(
            "SELECT CommandMessage FROM reactcommands WHERE CommandName = ?", cmd
        )
        if react_cmd != None:
            bot.send_message(react_cmd, channel)
        else:
            perform(bot, user, cmd, channel, *args)


def perform(bot, user, call, channel, *args):
    if call in ("help", "comands", "cmds"):
        misc.help(bot, bot.PREFIX, cmds, channel)

    else:
        for cmd in all_cmds:
            if call in cmd.callables:
                if time() > cmd.next_use:
                    cmd.func(bot, user, channel, *args)
                    cmd.next_use = time() + cmd.cooldown
                else:
                    pass

                return
