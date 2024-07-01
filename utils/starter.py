import os
import random
from utils.pixelverse import PixelVerse
from aiohttp.client_exceptions import ContentTypeError
from data import config
from utils.core import logger, get_all_lines
from itertools import zip_longest
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    pixel = PixelVerse(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await pixel.login():
        while True:
            try:
                available_points, end_time = await pixel.progress()

                await pixel.claim_daily_reward()
                await pixel.claim_daily_combo()

                if config.BUY_NEW_PETS:
                    balance, u_id = await pixel.get_me()
                    if await pixel.buy_pet(balance):
                        logger.success(f"Thread {thread} | {account} | Buy new pet")

                balance, u_id = await pixel.get_me()
                while True and config.AUTO_UPGRADE_PETS['ACTIVE']:
                    pet = await pixel.get_pet_for_upgrade(balance)
                    if not pet: break
                    pet = pet[0]
                    if await pixel.upgrade_pet(pet['id']):
                        balance -= pet['price']
                        logger.success(f"Thread {thread} | {account} | Upgraded pet {pet['name']} to {pet['level']} level! Balance: {balance}")
                        await asyncio.sleep(random.uniform(*config.DELAYS['UPGRADE_PET']))

                if pixel.current_time() > end_time or available_points > config.MIN_POINTS_TO_CLAIM:
                    claimed_points, end_time = await pixel.claim_points()
                    logger.success(f"Thread {thread} | {account} | Claimed {claimed_points} points!")

                if config.BATTLE['ACTIVE']:
                    await pixel.select_pet_for_battle()
                    await pixel.battle()

                    await asyncio.sleep(random.uniform(*config.DELAYS['BATTLE_DELAY']))

            except ContentTypeError as e:
                logger.error(f"Thread {thread} | {account} | Error: {e}")
                await asyncio.sleep(120)

            except Exception as e:
                logger.error(f"Thread {thread} | {account} | Error: {e}")
                await asyncio.sleep(5)

    else:
        await pixel.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []

    if config.PROXY['USE_PROXY_FROM_FILE']:
        proxys = get_all_lines(config.PROXY['PROXY_PATH'])
        for thread, (account, proxy) in enumerate(zip_longest(accounts, proxys)):
            if not account: break
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(PixelVerse(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))
    else:
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(PixelVerse(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Balance', 'Referrals', 'Referral link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
