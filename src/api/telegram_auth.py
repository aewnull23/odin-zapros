import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import HTTPException

from src.config import get_settings


def validate_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData per official docs."""
    settings = get_settings()
    if not settings.validate_init_data or not settings.bot_token:
        return dict(parse_qsl(init_data, keep_blank_values=True))

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash in initData")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated, received_hash):
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    if user_raw := parsed.get("user"):
        try:
            parsed["user"] = json.loads(user_raw)
        except json.JSONDecodeError:
            pass
    return parsed
