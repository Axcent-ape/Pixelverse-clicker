import json
import random
import time
from datetime import datetime
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent
from hmac import new
from hashlib import sha256


class PixelVerse:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"http://{proxy}" if proxy is not None else None

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPE,
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False))
        self.socket = self.session
        self.socket.headers.pop('Initdata', None)

    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        await self.login()

        r = await (await self.session.get("https://api-clicker.pixelverse.xyz/api/users", proxy=self.proxy)).json()
        balance = str(round(r.get('clicksCount'), 2))
        referral_link = "https://t.me/pixelversexyzbot?start=" + r.get('telegramUserId') if r.get('telegramUserId') is not None else '-'

        await asyncio.sleep(1)

        r = await (await self.session.get("https://api-clicker.pixelverse.xyz/api/points/burned-points/leaderboard", proxy=self.proxy)).json()
        referrals_count = str(r.get('currentUser').get('referralsCount'))

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'
        return [phone_number, name, balance, referrals_count, referral_link, proxy]

    async def claim_daily_combo(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/cypher-games/current', proxy=self.proxy)
        if resp.status == 400: return
        resp_json = await resp.json()

        combo_id = resp_json.get('id')
        options = resp_json.get('availableOptions')

        json_data = {item['id']: index for index, item in enumerate(random.sample(options, 4))}
        resp = await self.session.post(f"https://api-clicker.pixelverse.xyz/api/cypher-games/{combo_id}/answer", json=json_data, proxy=self.proxy)
        reward = (await resp.json()).get('rewardAmount')
        logger.success(f"Thread {self.thread} | {self.account} | Claim daily combo! Reward: {reward}")

    async def claim_daily_reward(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/daily-rewards', proxy=self.proxy)

        if (await resp.json()).get('todaysRewardAvailable'):
            resp = await self.session.post('https://api-clicker.pixelverse.xyz/api/daily-rewards/claim', proxy=self.proxy)
            r = await resp.json()
            logger.success(f"Thread {self.thread} | {self.account} | Claimed daily reward: {r.get('amount')}")

    async def upgrade_pet(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/pets', proxy=self.proxy)
        resp_json = await resp.json()

        expensive_pet = None
        for pet in resp_json.get('data'):
            if not expensive_pet:
                expensive_pet = [pet.get('userPet').get('levelUpPrice'), pet.get('userPet').get('id')]
            elif pet.get('userPet').get('levelUpPrice') > expensive_pet[0]:
                expensive_pet = [pet.get('userPet').get('levelUpPrice'), pet.get('userPet').get('id')]

        balance, u_id = await self.get_me()
        if balance >= expensive_pet[0]:

            resp = await self.session.post(f'https://api-clicker.pixelverse.xyz/api/pets/user-pets/{expensive_pet[1]}/level-up', proxy=self.proxy)
            return resp.status == 201

    async def get_pet(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/pets', proxy=self.proxy)
        resp_json = await resp.json()

        expensive_pet = None
        for pet in resp_json.get('data'):
            if not expensive_pet:
                expensive_pet = [pet.get('userPet').get('levelUpPrice'), pet.get('id')]
            elif pet.get('userPet').get('levelUpPrice') > expensive_pet[0]:
                expensive_pet = [pet.get('userPet').get('levelUpPrice'), pet.get('id')]

        return expensive_pet[1]

    async def select_pet(self):
        expensive_pet = await self.get_pet()
        resp = await self.session.post(f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{expensive_pet}/select", proxy=self.proxy)

    async def battle(self):
        if config.BATTLES['BATTLE_DELAY']:
            await asyncio.sleep(random.uniform(*config.BATTLES['BATTLE_DELAY']))

        balance, u_id = await self.get_me()
        ws = await self.socket.ws_connect('wss://api-clicker.pixelverse.xyz/socket.io/?EIO=4&transport=websocket', proxy=self.proxy)

        init_data = self.session.headers['Initdata']

        await ws.send_str(f'40{{"tg-id":{u_id},"secret":"{self.session.headers["Secret"]}","initData":"{init_data}"}}')

        battle_id = None
        hits = 0
        while True:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == '2':
                        await ws.send_str('3')

                    elif '42[' in msg.data:
                        m = json.loads(msg.data[2:])

                        if m[0] == 'START':
                            battle_id = m[1]['battleId']
                            logger.info(f"Thread {self.thread} | {self.account} | Started the battle! BattleId: {battle_id}")

                        if m[0] == 'SET_SUPER_HIT_ATTACK_ZONE':
                            await ws.send_str(f'42["SET_SUPER_HIT_ATTACK_ZONE",{{"battleId":"{battle_id}","zone":{random.randint(1, 4)}}}]')

                        if m[0] == 'SET_SUPER_HIT_DEFEND_ZONE':
                            await ws.send_str(f'42["SET_SUPER_HIT_DEFEND_ZONE",{{"battleId":"{battle_id}","zone":{random.randint(1, 4)}}}]')

                        if m[0] == 'END':
                            if m[1]['result'] == 'WIN':
                                logger.success(f"Thread {self.thread} | {self.account} | Win in battle! Hits made: {hits}. Reward: {m[1]['reward']}")
                            else:
                                logger.warning(f"Thread {self.thread} | {self.account} | Lost in battle! Lose: {m[1]['reward']}")
                            return

                    if battle_id:
                        await ws.send_str(f'42["HIT",{{"battleId":"{battle_id}"}}]')
                        hits += 1
                        await asyncio.sleep(random.uniform(*config.BATTLES['ATTACK_DELAY']))
            break

    @staticmethod
    def iso_to_unix_time(iso_time: str):
        return int(datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp()) + 1

    @staticmethod
    def current_time():
        return int(time.time())

    async def get_me(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/users', proxy=self.proxy)
        r = await resp.json()
        return r.get('clicksCount'), r.get('telegramUserId')

    async def progress(self):
        resp = await self.session.get('https://api-clicker.pixelverse.xyz/api/mining/progress', proxy=self.proxy)
        resp_json = await resp.json()

        return resp_json.get('currentlyAvailable'), self.iso_to_unix_time(resp_json.get('nextFullRestorationDate'))

    async def claim_points(self):
        resp = await self.session.post('https://api-clicker.pixelverse.xyz/api/mining/claim', proxy=self.proxy)
        resp_json = await resp.json()

        return round(resp_json.get('claimedAmount'), 2), self.iso_to_unix_time(resp_json.get('nextFullRestorationDate'))

    async def logout(self):
        await self.session.close()

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query, u_id = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        self.session.headers['Initdata'] = query
        self.session.headers['Secret'] = new("adwawdasfajfklasjglrejnoierjboivrevioreboidwa".encode(), u_id.encode(), sha256).hexdigest()
        self.session.headers['Tg-Id'] = u_id
        return True

    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            await self.client.send_message('pixelversexyzbot', '/start 6008239182')
            await asyncio.sleep(2)

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('pixelversexyzbot'),
                bot=await self.client.resolve_peer('pixelversexyzbot'),
                platform='android',
                from_bot_menu=False,
                url='https://sexyzbot.pxlvrs.io/#/'
            ))

            u_id = (await self.client.get_me()).id

            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}", str(u_id)
        except:
            return None, None
