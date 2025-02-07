import aiohttp

from postpuppy.utils.env import env


async def get_viewer_signature(email: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://shipment-viewer.hackclub.com/api/presign",
            data=email,
            headers={"Authorization": env.shipment_viewer_token},
        ) as resp:
            return await resp.text()
