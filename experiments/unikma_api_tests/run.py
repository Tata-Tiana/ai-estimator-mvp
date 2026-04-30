from __future__ import annotations

from pathlib import Path
import json

from config import REFERENCE_UNIKMA_DIR, SAMPLES_DIR
from logger import get_logger
from material_matcher import match_materials
from unikma_client import UnikmaClient


logger = get_logger()


def main() -> None:
    client = UnikmaClient()

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            print("Выход.")
            break

        try:
            if choice == "1":
                handle_get_nomenclature(client)
            elif choice == "2":
                handle_get_price_file(client)
            elif choice == "3":
                handle_get_stores(client)
            elif choice == "4":
                handle_material_match(client)
            elif choice == "5":
                handle_get_remains(client)
            else:
                print("Неизвестная команда. Выберите пункт из меню.")
        except Exception as exc:
            logger.exception("Command failed: %s", exc)
            print(f"Ошибка: {exc}")


def print_menu() -> None:
    print("\nТесты API УНИКМА")
    print("1 - Загрузить номенклатуру")
    print("2 - Скачать прайс Excel")
    print("3 - Показать склады")
    print("4 - Протестировать поиск материалов")
    print("5 - Получить остатки (пример)")
    print("0 - Выход")


def handle_get_nomenclature(client: UnikmaClient) -> None:
    raw_limit = input("Limit [100]: ").strip()
    limit = int(raw_limit) if raw_limit else 100
    data, file_path = client.get_nomenclature(limit=limit)
    print(f"Загружено позиций: {len(data)}")
    print(f"Сохранено: {file_path}")


def handle_get_price_file(client: UnikmaClient) -> None:
    file_path = client.get_price_file()
    print(f"Прайс сохранён: {file_path}")


def handle_get_stores(client: UnikmaClient) -> None:
    stores, file_path = client.get_stores()
    print(f"Сохранено: {file_path}")
    if not stores:
        print("Склады не найдены.")
        return

    for index, store in enumerate(stores[:10], start=1):
        name = store.get("Store", "Без названия")
        guid = store.get("GUID", "Без GUID")
        print(f"{index}. {name} [{guid}]")


def handle_material_match(client: UnikmaClient) -> None:
    materials = load_materials()
    nomenclature = load_latest_json("nomenclature")
    if nomenclature is None:
        print("Локальная номенклатура не найдена. Загружаю новую...")
        nomenclature, _ = client.get_nomenclature(limit=300)

    matches = match_materials(materials, nomenclature)
    for material, items in matches.items():
        print(f"\nМатериал: {material}")
        print("-> Найдено:")
        if not items:
            print("1. Совпадения не найдены")
            continue

        for index, item in enumerate(items, start=1):
            name = item.get("Name") or item.get("FullName") or "Без названия"
            code = item.get("Code") or item.get("FullCode") or "Без кода"
            print(f"{index}. {name} ({code})")


def handle_get_remains(client: UnikmaClient) -> None:
    nomenclature = load_latest_json("nomenclature")
    if nomenclature is None:
        print("Локальная номенклатура не найдена. Загружаю новую...")
        nomenclature, _ = client.get_nomenclature(limit=10)

    guids = [item.get("GUID") for item in nomenclature if item.get("GUID")]
    sample_guids = guids[:3]
    if not sample_guids:
        raise ValueError("Не удалось найти GUID товаров в номенклатуре.")

    remains, file_path = client.get_remains(sample_guids)
    print(f"Сохранено: {file_path}")
    print(f"Получено записей: {len(remains)}")


def load_materials() -> list[str]:
    file_path = SAMPLES_DIR / "materials.txt"
    with file_path.open("r", encoding="utf-8") as file_obj:
        return [line.strip() for line in file_obj if line.strip()]


def load_latest_json(prefix: str) -> list[dict] | None:
    files = sorted(REFERENCE_UNIKMA_DIR.glob(f"{prefix}_*.json"))
    if not files:
        return None

    latest_file = files[-1]
    with latest_file.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


if __name__ == "__main__":
    main()

