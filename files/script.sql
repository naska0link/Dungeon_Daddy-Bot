CREATE TABLE IF NOT EXISTS userbalance (
    UserID text PRIMARY KEY,
    UserName text,
    MessagesSent integer DEFAULT 0,
    Coins integer DEFAULT 0,
    Gems integer DEFAULT 0
);
CREATE TABLE IF NOT EXISTS coincooldowns (
    UserID text PRIMARY KEY,
    UserName text
);
CREATE TABLE IF NOT EXISTS gemcooldowns (
    UserID text PRIMARY KEY,
    UserName text
);
CREATE TABLE IF NOT EXISTS shop (
    ItemName text PRIMARY KEY,
    ItemCost integer,
    Currency text
);