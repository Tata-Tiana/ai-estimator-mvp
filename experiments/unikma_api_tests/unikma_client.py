from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import json

from config import BASE_URL, REFERENCE_UNIKMA_DIR, UNIKMA_API_KEY
from logger import get_logger


class UnikmaClient:
    def __init__(self, api_key: str | None = None, timeout: int = 60) -> None:
        self.api_key = (api_key or UNIKMA_API_KEY).strip()
        self.timeout = timeout
        self.logger = get_logger()
        REFERENCE_UNIKMA_DIR.mkdir(parents=True, exist_ok=True)

    def get_nomenclature(self, offset: int = 0, limit: int = 100) -> tuple[list[dict[str, Any]], Path]:
        response = self._request(
            "GET",
            "/GetNomenclatures/",
            params={"Offset": offset, "Limit": limit},
        )
        data = response.json()
        file_path = self._save_json("nomenclature", data)
        return data, file_path

    def get_price_file(self) -> Path:
        response = self._request("GET", "/GetPriceFile", stream=True)
        file_path = self._build_file_path("price_file", "xlsx")
        with file_path.open("wb") as file_obj:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_obj.write(chunk)
        self.logger.info("Saved price file to %s", file_path)
        return file_path

    def get_stores(self) -> tuple[list[dict[str, Any]], Path]:
        response = self._request("GET", "/GetStores/")
        data = response.json()
        file_path = self._save_json("stores", data)
        return data, file_path

    def get_remains(self, tovars: list[str]) -> tuple[list[dict[str, Any]], Path]:
        payload = {"Tovars": tovars}
        response = self._request("POST", "/GetRemain/", json_body=payload)
        data = response.json()
        file_path = self._save_json("remains", data)
        return data, file_path

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> Any:
        if not self.api_key:
            raise ValueError("UNIKMA_API_KEY is empty. Add it to your .env file.")

        try:
            import requests
        except ImportError as exc:
            raise ImportError("The 'requests' package is required. Install project dependencies first.") from exc

        url = f"{BASE_URL}{endpoint}"
        request_params = {"api_key": self.api_key}
        if params:
            request_params.update(params)

        self.logger.info("Request %s %s", method, url)
        if request_params:
            self.logger.info("Params: %s", request_params)
        if json_body:
            self.logger.info("JSON body: %s", json_body)

        try:
            response = requests.request(
                method=method,
                url=url,
                params=request_params,
                json=json_body,
                timeout=self.timeout,
                stream=stream,
            )
            response.raise_for_status()
            self.logger.info("Response status: %s", response.status_code)
            return response
        except requests.RequestException as exc:
            self.logger.exception("HTTP error while calling %s: %s", url, exc)
            raise

    def _save_json(self, prefix: str, data: Any) -> Path:
        file_path = self._build_file_path(prefix, "json")
        with file_path.open("w", encoding="utf-8") as file_obj:
            json.dump(data, file_obj, ensure_ascii=False, indent=2)
        self.logger.info("Saved JSON response to %s", file_path)
        return file_path

    def _build_file_path(self, prefix: str, suffix: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return REFERENCE_UNIKMA_DIR / f"{prefix}_{timestamp}.{suffix}"
