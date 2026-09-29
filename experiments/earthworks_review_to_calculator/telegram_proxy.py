from __future__ import annotations

import os
from collections.abc import Mapping
from urllib.parse import quote


_PROXY_KEYS = (
    "TELEGRAM_PROXY_HOST",
    "TELEGRAM_PROXY_PORT",
    "TELEGRAM_PROXY_USERNAME",
    "TELEGRAM_PROXY_PASSWORD",
)


def build_telegram_proxy(environ: Mapping[str, str] | None = None) -> dict[str, str] | None:
    values = environ if environ is not None else os.environ
    config = {key: values.get(key, "").strip() for key in _PROXY_KEYS}
    if not any(config.values()):
        return None

    missing = [key for key, value in config.items() if not value]
    if missing:
        raise ValueError("incomplete Telegram proxy configuration; missing: " + ", ".join(missing))

    host = config["TELEGRAM_PROXY_HOST"]
    if any(character.isspace() for character in host) or "://" in host or "/" in host:
        raise ValueError("TELEGRAM_PROXY_HOST must contain only a hostname or IP address")

    try:
        port = int(config["TELEGRAM_PROXY_PORT"])
    except ValueError as exc:
        raise ValueError("TELEGRAM_PROXY_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise ValueError("TELEGRAM_PROXY_PORT must be between 1 and 65535")

    username = quote(config["TELEGRAM_PROXY_USERNAME"], safe="")
    password = quote(config["TELEGRAM_PROXY_PASSWORD"], safe="")
    proxy_url = f"socks5h://{username}:{password}@{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}


def configure_telegram_proxy(apihelper, environ: Mapping[str, str] | None = None) -> bool:
    proxy = build_telegram_proxy(environ)
    if proxy is None:
        return False
    apihelper.proxy = proxy
    return True
