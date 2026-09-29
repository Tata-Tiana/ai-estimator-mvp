from __future__ import annotations

import asyncio
import importlib.util
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram.ext import CommandHandler, MessageHandler


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "earthworks_review_to_calculator"
    / "telegram_ptb_transport.py"
)
SPEC = importlib.util.spec_from_file_location("telegram_ptb_transport", MODULE_PATH)
assert SPEC and SPEC.loader
transport_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transport_module)


def test_registers_command_and_document_handlers() -> None:
    bot = transport_module.TeleBot("123456:TEST_TOKEN")

    @bot.message_handler(commands=["start", "help"])
    def command_handler(_message) -> None:
        return None

    @bot.message_handler(content_types=["document"])
    def document_handler(_message) -> None:
        return None

    application = bot._build_application()
    handlers = [handler for group in application.handlers.values() for handler in group]

    assert sum(isinstance(handler, CommandHandler) for handler in handlers) == 1
    assert sum(isinstance(handler, MessageHandler) for handler in handlers) == 1


def test_sync_api_bridge_sends_replies_and_documents() -> None:
    async def scenario() -> None:
        bot = transport_module.TeleBot("123456:TEST_TOKEN")
        ptb_bot = SimpleNamespace(
            send_message=AsyncMock(return_value="message"),
            send_document=AsyncMock(return_value="document"),
        )
        application = SimpleNamespace(bot=ptb_bot)
        bot._application = application
        bot._loop = asyncio.get_running_loop()
        message = SimpleNamespace(chat=SimpleNamespace(id=42), message_id=7)

        reply = await asyncio.to_thread(bot.reply_to, message, "hello")
        sent = await asyncio.to_thread(bot.send_document, 42, b"xlsx", caption="ready")

        assert reply == "message"
        assert sent == "document"
        ptb_bot.send_message.assert_awaited_once_with(
            chat_id=42,
            text="hello",
            reply_to_message_id=7,
            parse_mode=None,
        )
        ptb_bot.send_document.assert_awaited_once_with(
            chat_id=42,
            document=b"xlsx",
            caption="ready",
            parse_mode=None,
        )

    asyncio.run(scenario())


def test_sync_api_bridge_downloads_file_bytes() -> None:
    async def scenario() -> None:
        telegram_file = SimpleNamespace(
            file_path="documents/input.json",
            download_as_bytearray=AsyncMock(return_value=bytearray(b"{}")),
        )
        ptb_bot = SimpleNamespace(get_file=AsyncMock(return_value=telegram_file))
        bot = transport_module.TeleBot("123456:TEST_TOKEN")
        bot._application = SimpleNamespace(bot=ptb_bot)
        bot._loop = asyncio.get_running_loop()

        file_info = await asyncio.to_thread(bot.get_file, "file-id")
        payload = await asyncio.to_thread(bot.download_file, file_info.file_path)

        assert payload == b"{}"
        ptb_bot.get_file.assert_awaited_once_with("file-id")
        telegram_file.download_as_bytearray.assert_awaited_once_with()

    asyncio.run(scenario())


def test_startup_callbacks_run_once_and_can_send_messages() -> None:
    async def scenario() -> None:
        ptb_bot = SimpleNamespace(send_message=AsyncMock(return_value="sent"))
        application = SimpleNamespace(bot=ptb_bot)
        bot = transport_module.TeleBot("123456:TEST_TOKEN")
        calls: list[str] = []

        def startup() -> None:
            calls.append("startup")
            bot.send_message(42, "recovered")

        bot.add_startup_callback(startup)
        await bot._post_init(application)
        await bot._post_init(application)

        assert calls == ["startup"]
        ptb_bot.send_message.assert_awaited_once_with(
            chat_id=42,
            text="recovered",
            parse_mode=None,
        )

    asyncio.run(scenario())


def test_secret_filter_redacts_message_and_sensitive_traceback() -> None:
    secret_filter = transport_module._SecretFilter(("BOT_TOKEN", "socks5://user:password@proxy"))
    record = logging.LogRecord(
        name="httpx",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="request BOT_TOKEN via socks5://user:password@proxy",
        args=(),
        exc_info=None,
    )

    assert secret_filter.filter(record) is True
    assert "BOT_TOKEN" not in record.getMessage()
    assert "user:password" not in record.getMessage()
