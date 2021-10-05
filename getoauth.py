import os
import requests
from dotenv import load_dotenv


def getoauth_tokens():
    load_dotenv("token.env")
    CLIENT_ID = os.getenv('CLIENT_ID')
    SECRET = os.getenv('SECRET')
    tokens, refresh_tokens = [], []
    for streamer_code in os.getenv('CODES').split(','):
        print(streamer_code)
        (channel, code) = streamer_code.split(':')
        try:
            token = requests.post(
                f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={SECRET}&code={code}&grant_type=authorization_code&redirect_uri=http://localhost"
            )
            print(token.json())
            token = token.json()
            ref_token = token['refresh_token']
            acc_token = token['access_token']
        except:
            ref_token = "none"
            acc_token = "none"
        tokens.append(f"{channel}:{acc_token}")
        refresh_tokens.append(f"{channel}:{ref_token}")
    file = ""
    with open("token.env", 'r', encoding="utf-8") as f:
        env = f.read()
        file = []
        for splt in env.split('\n'):
            if splt[0:13] == "ACCESS_TOKEN=":
                file.append("ACCESS_TOKEN=" + ','.join(tokens))
            elif splt[0:14] == "REFRESH_CODES=":
                file.append("REFRESH_CODES=" + ','.join(refresh_tokens))
            else:
                file.append(splt)
        file = '\n'.join(file)
    with open("token.env", 'w', encoding="utf-8") as f:
        f.write(file)


def refresh_token():
    load_dotenv("token.env")
    CLIENT_ID = os.getenv('CLIENT_ID')
    SECRET = os.getenv('SECRET')
    REFRESH_CODES = os.getenv('REFRESH_CODES').split(',')
    tokens, refresh_tokens = [], []
    for streamer_code in REFRESH_CODES:
        (channel, code) = streamer_code.split(':')
        # print(streamer_code)
        try:
            token = requests.post(
                f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={SECRET}&refresh_token={code}&grant_type=refresh_token&redirect_uri=http://localhost"
            )
            # print(token.json())
            token = token.json()
            ref_token = token['refresh_token']
            acc_token = token['access_token']
        except:
            ref_token = "none"
            acc_token = "none"
        tokens.append(f"{channel}:{acc_token}")
        refresh_tokens.append(f"{channel}:{ref_token}")
    file = ""
    with open("token.env", 'r', encoding="utf-8") as f:
        env = f.read()
        file = []
        for splt in env.split('\n'):
            if splt[0:13] == "ACCESS_TOKEN=":
                file.append("ACCESS_TOKEN=" + ','.join(tokens))
            elif splt[0:14] == "REFRESH_CODES=":
                file.append("REFRESH_CODES=" + ','.join(refresh_tokens))
            else:
                file.append(splt)
        file = '\n'.join(file)
    with open("token.env", 'w', encoding="utf-8") as f:
        f.write(file)
    return {keypair.split(':')[0]: keypair.split(':')[1] for keypair in tokens}


def getoauth_token():
    load_dotenv("token.env")
    return {
        keypair.split(':')[0]: keypair.split(':')[1]
        for keypair in os.getenv('ACCESS_TOKEN').split(',')
    }


if __name__ == '__main__':
    getoauth_tokens()
    # print(refresh_token())
    # print(getoauth_token())