# api id, hash
API_ID = 1488
API_HASH = 'abcde1488'

DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'BATTLE_DELAY': [5, 10],  # delay between battles
    'ATTACK_DELAY': [0.085, 0.09],  # delay between attacks in battle
    'UPGRADE_PET': [1, 3]   # delay after pet upgrade
}

AUTO_UPGRADE_PETS = {
    'ACTIVE': True,
    'MAX_UPGRADE_LEVEL': 38,    # maximum level to upgrade pets
}

BATTLE = {
    'ACTIVE': True,                   # True - play in battle, False - no play in battle
    'BEST_PARAMETER_PETS': "MAX_ENERGY",  # what's the best parameter to choose a pet by. Available: "MAX_ENERGY", "DAMAGE"

}

PROXY = {
    "USE_PROXY_FROM_FILE": True,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "socks5",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "socks5"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

# minimum count of points to collect
MIN_POINTS_TO_CLAIM: int = 12000

# True - to buy new pets
BUY_NEW_PETS = True

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = f"""{"PixelTap by Pixelverse".center(40)}
Soft for https://t.me/pixelversexyzbot collects daily rewards;
saves the results of each daily combo selection to the account to get the correct sequence of cards;
collects points if they are greater than {MIN_POINTS_TO_CLAIM};
improves a random pet if its level is less than {AUTO_UPGRADE_PETS['MAX_UPGRADE_LEVEL']};
selects the best pet by {BATTLE['BEST_PARAMETER_PETS']}; 
attacks in battles every {DELAYS['ATTACK_DELAY']} seconds.

The software also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}

To buy this soft with the option to set your referral link write me: https://t.me/Axcent_ape
"""
