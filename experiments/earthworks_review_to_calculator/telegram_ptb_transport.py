from __future__ import annotations

import asyncio
import logging
import threading
import traceback
from collections.abc import Callable, Coroutine
from types import SimpleNamespace
from typing import Any

from telegram import Document, Message, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest


types = SimpleNamespace(Message=Message, Document=Document)

_LOGGER = logging.getLogger(__name__)
_Handler = Callable[[Message], None]
_StartupCallback = Callable[[], None]


class _SecretFilter(logging.Filter):
    def __init__(self, secrets: tuple[str, ...]):
        super().__init__()
        self._secrets = tuple(secret for secret in secrets if secret)

    def _redact(self, value: str) -> str:
        for secret in self._secrets:
            value = value.replace(secret, "[REDACTED]")
        return value

    def filter(self, record: logging.LogRecord) -> bool:
        message = self._redact(record.getMessage())
        record.msg = message
        record.args = ()
        if record.exc_info:
            exception_text = "".join(traceback.format_exception(*record.exc_info))
            if any(secret in exception_text for secret in self._secrets):
                record.exc_info = None
                record.exc_text = None
                record.msg = f"{message} [exception details redacted]"
        return True


class TeleBot:
    """Synchronous handler facade backed by python-telegram-bot and HTTPX.

    The existing estimator handlers perform long synchronous subprocess and file
    operations. PTB dispatches each of them to a worker thread, while every
    Telegram API call is submitted back to PTB's event loop. This keeps polling
    responsive without rewriting the calculator and job orchestration code.
    """

    def __init__(self, token: str, parse_mode: str | None = None, proxy_url: str | None = None):
        self.token = token
        self.parse_mode = parse_mode
        self.proxy_url = proxy_url
        self._handler_specs: list[tuple[str, tuple[str, ...], _Handler]] = []
        self._startup_callbacks: list[_StartupCallback] = []
        self._application: Application | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._file_cache: dict[str, Any] = {}
        self._startup_callbacks_completed = False
        self._state_lock = threading.RLock()

    def message_handler(
        self,
        *,
        commands: list[str] | tuple[str, ...] | None = None,
        content_types: list[str] | tuple[str, ...] | None = None,
    ) -> Callable[[_Handler], _Handler]:
        if bool(commands) == bool(content_types):
            raise ValueError("exactly one of commands or content_types must be provided")

        kind = "commands" if commands else "content_types"
        values = tuple(commands or content_types or ())

        def decorator(callback: _Handler) -> _Handler:
            self._handler_specs.append((kind, values, callback))
            return callback

        return decorator

    def add_startup_callback(self, callback: _StartupCallback) -> None:
        self._startup_callbacks.append(callback)

    def _runtime(self) -> tuple[asyncio.AbstractEventLoop, Application]:
        with self._state_lock:
            loop = self._loop
            application = self._application
        if loop is None or application is None or not loop.is_running():
            raise RuntimeError("Telegram transport is not running")
        return loop, application

    def _submit(self, operation: Callable[[Application], Coroutine[Any, Any, Any]]) -> Any:
        loop, application = self._runtime()
        future = asyncio.run_coroutine_threadsafe(operation(application), loop)
        return future.result()

    def reply_to(self, message: Message, text: str, **kwargs: Any) -> Message:
        return self._submit(
            lambda application: application.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_to_message_id=message.message_id,
                parse_mode=self.parse_mode,
                **kwargs,
            )
        )

    def send_message(self, chat_id: int, text: str, **kwargs: Any) -> Message:
        return self._submit(
            lambda application: application.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=self.parse_mode,
                **kwargs,
            )
        )

    def send_document(self, chat_id: int, document: Any, caption: str | None = None, **kwargs: Any) -> Message:
        return self._submit(
            lambda application: application.bot.send_document(
                chat_id=chat_id,
                document=document,
                caption=caption,
                parse_mode=self.parse_mode,
                **kwargs,
            )
        )

    def get_file(self, file_id: str) -> Any:
        telegram_file = self._submit(lambda application: application.bot.get_file(file_id))
        cache_key = telegram_file.file_path or file_id
        with self._state_lock:
            self._file_cache[cache_key] = telegram_file
        return telegram_file

    def download_file(self, file_path: str) -> bytes:
        with self._state_lock:
            telegram_file = self._file_cache.pop(file_path, None)
        if telegram_file is None:
            raise RuntimeError("Telegram file was not requested with get_file before download_file")
        data = self._submit(lambda _application: telegram_file.download_as_bytearray())
        return bytes(data)

    async def _dispatch_sync_handler(
        self,
        callback: _Handler,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        message = update.effective_message
        if message is None:
            return
        await asyncio.to_thread(callback, message)

    async def _post_init(self, application: Application) -> None:
        with self._state_lock:
            self._application = application
            self._loop = asyncio.get_running_loop()
            run_startup_callbacks = not self._startup_callbacks_completed
        if run_startup_callbacks:
            for callback in self._startup_callbacks:
                await asyncio.to_thread(callback)
            with self._state_lock:
                self._startup_callbacks_completed = True

    async def _error_handler(self, _update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        error = context.error
        error_text = str(error).replace(self.token, "[REDACTED]") if error else "unknown error"
        _LOGGER.error("PTB update handler failed with %s: %s", type(error).__name__, error_text)

    def _request(self) -> HTTPXRequest:
        return HTTPXRequest(
            proxy=self.proxy_url,
            connect_timeout=20.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=10.0,
            media_write_timeout=120.0,
        )

    def _protect_logs(self) -> None:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        secret_filter = _SecretFilter((self.token, self.proxy_url or ""))
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(secret_filter)

    def _build_application(self) -> Application:
        # The production bots share one HTTPXRequest between Bot API calls and
        # getUpdates. Keep the same transport/pool layout for proxy parity.
        request = self._request()
        builder = (
            ApplicationBuilder()
            .token(self.token)
            .request(request)
            .get_updates_request(request)
            .post_init(self._post_init)
        )
        application = builder.build()

        for kind, values, callback in self._handler_specs:
            async def wrapped(
                update: Update,
                context: ContextTypes.DEFAULT_TYPE,
                _callback: _Handler = callback,
            ) -> None:
                await self._dispatch_sync_handler(_callback, update, context)

            if kind == "commands":
                application.add_handler(CommandHandler(values, wrapped, block=False))
                continue
            unsupported = set(values) - {"document"}
            if unsupported:
                raise ValueError(f"unsupported PTB content types: {sorted(unsupported)}")
            application.add_handler(MessageHandler(filters.Document.ALL, wrapped, block=False))

        application.add_error_handler(self._error_handler, block=False)
        return application

    def infinity_polling(self, timeout: int = 10, long_polling_timeout: int = 5) -> None:
        del timeout  # PTB configures request timeouts in HTTPXRequest.
        self._protect_logs()
        application = self._build_application()
        with self._state_lock:
            self._application = application
        try:
            application.run_polling(
                poll_interval=0.0,
                timeout=long_polling_timeout,
                bootstrap_retries=3,
                drop_pending_updates=False,
                close_loop=False,
            )
        finally:
            with self._state_lock:
                self._loop = None
                self._application = None
                self._file_cache.clear()
