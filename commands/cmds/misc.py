def help(bot, prefix, cmds, channel):
    bot.send_message(
        f"Registered commands: "
        + ", ".join(
            [
                f"{prefix}{cmd.callables[0]}"
                for cmd in sorted(cmds, key=lambda cmd: cmd.callables[0])
            ]
        ),
        channel,
    )
    bot.send_message(
        f"Registered commands (incl. aliases): "
        + ", ".join(
            [
                f"{prefix}{'/'.join(cmd.callables)}"
                for cmd in sorted(cmds, key=lambda cmd: cmd.callables[0])
            ]
        ),
        channel,
    )


def hello(bot, user, channel, *args):
    bot.send_message(f"Hey {user['name']}", channel)


def delete_msg(bot, user, channel, *args):
    bot.send_message(f"/delete {user['msgid']}", channel)


def copyright(bot, user, channel, *args):
    if int(user["id"]) in bot.CHANNEL_IDS_LIST:
        bot.send_message_all(
            "Twitchpaign is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC."
        )
