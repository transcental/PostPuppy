import binascii
import os
from datetime import datetime
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from postpuppy.utils.env import env
from postpuppy.utils.logging import send_heartbeat


async def send_email(recipient: str, subject: str, msg: MIMEText):
    await send_heartbeat(
        f"{recipient}: Sending email",
        [f"Subject: {subject}", f"Message: {msg.as_string()}"],
    )
    env.smtp_login()
    mail = MIMEMultipart()
    mail["From"] = f"Post Puppy <{env.smtp_sender}>"
    mail["To"] = recipient
    mail["Subject"] = subject

    mail.attach(msg)
    env.smtp_client.send_message(mail)
    await send_heartbeat(f"{recipient}: Email sent")

    return True


async def send_verification_link(user_id: str, email: str):
    await send_heartbeat(f"{user_id}: Generating verification email for {email}")
    signature = binascii.hexlify(os.urandom(32))
    nice_sig = signature.decode("utf-8")
    link = f"{env.domain}/verify?user_id={user_id}&email={email}&signature={nice_sig}"

    html_msg = f"""
<h1>Verify your email</h1>
<p>Click the link below to verify your email address</p>
<a href="{link}">Verify</a>
<span><em>This link will expire in 24 hours</em></span>

<p>This email was sent courtesy of Post Puppy! wrrf, wrrf</p>
"""

    expiry = datetime.now() + timedelta(hours=24)
    await env.db.user.update(
        where={"id": user_id},
        data={
            "emailSignature": str(nice_sig),
            "emailSignatureExpiry": expiry,
            "email": email,
        },
    )
    msg = MIMEText(html_msg, "html")
    await send_email(email, "Verify your email", msg)
