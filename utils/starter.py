import os
from utils.pixelverse import PixelVerse
from aiohttp.client_exceptions import ContentTypeError
from data import config
from utils.core import logger
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

                if pixel.current_time() > end_time or available_points > 12000:
                    claimed_points, end_time = await pixel.claim_points()
                    logger.success(f"Thread {thread} | {account} | Claimed {claimed_points} points!")

                if await pixel.upgrade_pet():
                    logger.success(f"Thread {thread} | {account} | Upgrade pet")

                await pixel.select_pet()
                if config.BATTLES['THREADED_BATTLES']:
                    await asyncio.gather(*[asyncio.create_task(pixel.battle()) for i in range(config.BATTLES['THREADS'])])
                else:
                    await pixel.battle()

                await asyncio.sleep(10)

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
