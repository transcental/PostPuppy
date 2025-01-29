import hashlib
import hmac

from postpuppy.utils.env import env


def sign(text: str):
    signing_secret = env.signing_secret
    h = hmac.new(signing_secret.encode(), text.encode(), hashlib.sha256)
    return h.hexdigest()


def check_signature(email: str, sig: str):
    return sig == sign(email)
