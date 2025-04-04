import asyncio
import binascii
import os
from datetime import datetime
from datetime import timedelta

from postpuppy.utils.env import env
from postpuppy.utils.logging import send_heartbeat


async def send_verification_link(user_id: str, email: str, language: dict):
    await send_heartbeat(f"{user_id}: Generating verification email for {email}")
    signature = binascii.hexlify(os.urandom(32))
    nice_sig = signature.decode("utf-8")
    link = f"{env.domain}/verify?user_id={user_id}&email={email}&signature={nice_sig}"

    async with env.aiohttp_session.post(
        "https://app.loops.so/api/v1/transactional",
        json={
            "email": email,
            "transactionalId": env.loops_transactional_id,
            "dataVariables": {
                "appName": language["display_name"],
                "verifyUrl": link,
                "noise": language["noise"],
                "sender": language["sender"],
            },
        },
    ) as res:
        if res.status != 200:
            await send_heartbeat(
                f"{user_id}: Failed to send verification email to {email}",
                [f"```{res.status}```"],
            )
            await asyncio.sleep(5)
            await send_verification_link(user_id, email, language)
            return

    expiry = datetime.now() + timedelta(hours=24)
    await env.db.user.update(
        where={"id": user_id},
        data={
            "emailSignature": str(nice_sig),
            "emailSignatureExpiry": expiry,
            "email": email,
        },
    )
