from .. import db
import math
import requests


def balance(bot, user, channel, *args):
    coins = db.field("SELECT Coins FROM userbalance WHERE UserID = ?", user["id"])
    gems = db.field("SELECT Gems FROM userbalance WHERE UserID = ?", user["id"])
    bot.send_message(
        f"{user['name']}, you have {coins:,} coins and {gems:,} gems.", channel
    )


def add_shop(bot, user, channel, item=None, cost=None, currency=None, *args):
    currency = (
        currency[0].upper() + currency[1:]
        if currency.lower() in ["gem", "coin"]
        else None
    )
    item = (item.replace(" ", "_")).lower() if item != None else None
    print(item, cost, currency)
    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (
        item != None and cost != None and currency != None
    ):

        db.execute(
            f"INSERT OR IGNORE INTO shop (ItemName, ItemCost, Currency) VALUES (?, ?, ?)",
            item,
            cost,
            currency,
        )
        bot.send_message(f"{item} has been added for {cost} {currency}.", channel)


def edit_shop(bot, user, channel, item=None, cost=None, currency=None, *args):
    currency = (
        currency[0].upper() + currency[1:]
        if currency.lower() in ["gem", "coin"]
        else None
    )
    item = (item.replace(" ", "_")).lower() if item != None else None

    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (
        item != None and cost != None and currency != None
    ):

        db.execute(
            f"UPDATE shop SET ItemCost = ?, Currency = ? WHERE ItemName = ?",
            cost,
            currency,
            item,
        )
        bot.send_message(f"{item} has been edited for {cost} {currency}.", channel)


def remove_shop(bot, user, channel, item=None, *args):
    item = (item.replace(" ", "_")).lower() if item != None else None

    if (int(user["id"]) in bot.CHANNEL_IDS_LIST) and (item != None):
        db.execute(f"DELETE FROM shop WHERE ItemName = ?", item)
        bot.send_message(f"{item} has been removed.", channel)


def display_shop(bot, user, channel, page=None, *args):
    try:
        page = 0 if page == None else int(page) - 1
    except:
        return
    shop_length = db.field("SELECT COUNT(*) FROM shop")
    shop_page_len = math.ceil(int(shop_length) / 10)
    item_start = page * 10
    item_end = page + 10
    if (item_start) > int(shop_length):
        pass
    else:
        shop_items = db.records(f"SELECT * FROM shop LIMIT {item_start}, {item_end}")
        items = ", ".join(
            [f"{item[0].replace('_', ' ')} {item[1]} {item[2]}" for item in shop_items]
        )
        bot.send_message(f"Page {page + 1} of {shop_page_len}: {items}", channel)


def purchase(bot, user, channel, item=None, amount=None, *args):
    amount = 1 if amount == None else int(amount)
    coins = db.field("SELECT Coins FROM userbalance WHERE UserID = ?", user["id"])
    gems = db.field("SELECT Gems FROM userbalance WHERE UserID = ?", user["id"])
    cost = (
        db.field("SELECT ItemCost FROM shop WHERE ItemName = ?", item.lower())
        if item != None
        else None
    )
    currency = (
        db.field("SELECT Currency FROM shop WHERE ItemName = ?", item.lower())
        if item != None
        else None
    )
    bal = int(coins) if currency == "Coin" else int(gems) if currency == "Gem" else None
    if cost is None:
        bot.send_message(f"{item} is not an item in the store.", channel)
    elif amount <= 0:
        pass
    elif bal < (int(cost) * int(amount)):
        # print("No")
        bot.send_message(
            f"{item} cost more then your petty {bal} {currency}s.", channel
        )
    else:
        bot.send_message(
            f"{item} has been purchased for {(int(cost) * amount)} {currency}.", channel
        )
        db.execute(
            f"UPDATE userbalance SET {currency}s = {currency}s - ? WHERE UserID = ?",
            (cost * amount),
            user["id"],
        )
        bot.discord_log({
                "content": f"{user['name']} has purchased {item} for {(int(cost) * amount)} {currency}."
            })
