# api id, hash
API_ID = 1488
API_HASH = 'abcd1488'

DELAYS = {
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
}

BATTLES = {
    'BATTLE_DELAY': [5, 10],  # delay between battles
    'ATTACK_DELAY': [0.085, 0.09],  # delay between attacks
    'THREADED_BATTLES': False,  # battles in multi threads
    'THREADS': 2,  # threads of battles
}

# proxy type for tg client
PROXY_TYPE = "http"  # "socks4", "socks5" and "http" are supported

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
