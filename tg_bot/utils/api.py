import aiohttp


async def connect_tg_account(user_id, tg_user_id):
    url = "http://app:8000/users/connect-tg"
    params = {"user_id": user_id, "tg_user_id": tg_user_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params) as response:
            return await response.json()
