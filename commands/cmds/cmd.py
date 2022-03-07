from .. import db


def add_command(bot, user, channel, name=None, response=None, *args):
    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (name != None
                                                      and response != None):
        name = name[1:].lower() if name.startswith(
            bot.PREFIX) else name.lower()
        db.execute(
            f"INSERT OR IGNORE INTO reactcommands (CommandName, CommandMessage) VALUES (?, ?)",
            name, response)
        bot.send_message(f"{name} has been added. {response}", channel)


def edit_command(bot, user, channel, name=None, response=None, *args):
    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (name != None
                                                      and response != None):
        name = name[1:].lower() if name.startswith(
            bot.PREFIX) else name.lower()
        db.execute(
            f"UPDATE reactcommands SET CommandMessage = ? WHERE CommandName = ?",
            response, name)
        bot.send_message(f"{name} has been updated. {response}", channel)


def remove_command(bot, user, channel, name=None, *args):
    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (name != None):
        name = name[1:].lower() if name.startswith(
            bot.PREFIX) else name.lower()
        db.execute(f"DELETE FROM reactcommands WHERE CommandName = ?", name)
        bot.send_message(f"{name} has been removed.", channel)
