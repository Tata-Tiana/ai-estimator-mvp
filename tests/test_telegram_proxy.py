from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "earthworks_review_to_calculator"
    / "telegram_proxy.py"
)
SPEC = importlib.util.spec_from_file_location("telegram_proxy", MODULE_PATH)
assert SPEC and SPEC.loader
telegram_proxy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(telegram_proxy)


def test_proxy_is_optional() -> None:
    assert telegram_proxy.build_telegram_proxy({}) is None


def test_proxy_credentials_are_url_encoded() -> None:
    proxy = telegram_proxy.build_telegram_proxy(
        {
            "TELEGRAM_PROXY_HOST": "82.117.86.224",
            "TELEGRAM_PROXY_PORT": "63475",
            "TELEGRAM_PROXY_USERNAME": "user+name",
            "TELEGRAM_PROXY_PASSWORD": "p@ss:word",
        }
    )

    expected = "socks5h://user%2Bname:p%40ss%3Aword@82.117.86.224:63475"
    assert proxy == {"http": expected, "https": expected}


def test_http_proxy_is_supported() -> None:
    proxy = telegram_proxy.build_telegram_proxy(
        {
            "TELEGRAM_PROXY_SCHEME": "http",
            "TELEGRAM_PROXY_HOST": "proxy.example",
            "TELEGRAM_PROXY_PORT": "8080",
            "TELEGRAM_PROXY_USERNAME": "user",
            "TELEGRAM_PROXY_PASSWORD": "secret",
        }
    )

    expected = "http://user:secret@proxy.example:8080"
    assert proxy == {"http": expected, "https": expected}


@pytest.mark.parametrize(
    "config",
    [
        {"TELEGRAM_PROXY_HOST": "82.117.86.224"},
        {
            "TELEGRAM_PROXY_HOST": "82.117.86.224",
            "TELEGRAM_PROXY_PORT": "not-a-port",
            "TELEGRAM_PROXY_USERNAME": "user",
            "TELEGRAM_PROXY_PASSWORD": "secret",
        },
        {
            "TELEGRAM_PROXY_HOST": "https://82.117.86.224",
            "TELEGRAM_PROXY_PORT": "63475",
            "TELEGRAM_PROXY_USERNAME": "user",
            "TELEGRAM_PROXY_PASSWORD": "secret",
        },
        {
            "TELEGRAM_PROXY_SCHEME": "mtp",
            "TELEGRAM_PROXY_HOST": "82.117.86.224",
            "TELEGRAM_PROXY_PORT": "63475",
            "TELEGRAM_PROXY_USERNAME": "user",
            "TELEGRAM_PROXY_PASSWORD": "secret",
        },
    ],
)
def test_invalid_proxy_configuration_is_rejected(config: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        telegram_proxy.build_telegram_proxy(config)


def test_configure_applies_proxy_without_logging_credentials() -> None:
    class ApiHelper:
        proxy = None

    helper = ApiHelper()
    enabled = telegram_proxy.configure_telegram_proxy(
        helper,
        {
            "TELEGRAM_PROXY_HOST": "proxy.example",
            "TELEGRAM_PROXY_PORT": "1080",
            "TELEGRAM_PROXY_USERNAME": "user",
            "TELEGRAM_PROXY_PASSWORD": "secret",
        },
    )

    assert enabled is True
    assert helper.proxy["https"].startswith("socks5h://")
