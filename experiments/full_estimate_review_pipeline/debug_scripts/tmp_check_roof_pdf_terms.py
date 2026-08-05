from pathlib import Path

import fitz


FILES = {
    "АРК КР1": "/Users/tatanamedzidova/Desktop/АРК КР1 для ИИ.pdf",
    "АРК КР2": "/Users/tatanamedzidova/Desktop/АРК КР2 для ИИ.pdf",
    "ТРЦ КР1": "/Users/tatanamedzidova/Desktop/КР-1_ТРЦ _01,07,2026.pdf",
    "ТРЦ КР2": "/Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,07,2026.pdf",
    "ЮСВ КР1": "/Users/tatanamedzidova/Desktop/ЮСВ КР1 (1).pdf",
    "ЮСВ КР2": "/Users/tatanamedzidova/Desktop/ЮСВ КР2 (11).pdf",
}

TERMS = [
    "кровл",
    "slope",
    "уклон",
    "вентшах",
    "венткан",
    "вк",
    "отверст",
    "пробивк",
    "воронк",
    "аэратор",
]


for name, path in FILES.items():
    print(f"\nFILE {name}: {Path(path).name}")
    doc = fitz.open(path)
    for page_number, page in enumerate(doc, 1):
        text = page.get_text("text") or ""
        low = text.lower()
        if not any(term in low for term in TERMS):
            continue

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        hits = [
            line
            for line in lines
            if any(term in line.lower() for term in TERMS)
        ]
        print(f" page {page_number}:")
        for hit in hits[:22]:
            print(f"   {hit[:240]}")


print("\n\nDETAIL ROOF PAGES")
DETAIL_PAGES = {
    "АРК КР2": ("/Users/tatanamedzidova/Desktop/АРК КР2 для ИИ.pdf", [23, 24, 25]),
    "ТРЦ КР2": ("/Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,07,2026.pdf", [21, 39, 40]),
    "ЮСВ КР2": ("/Users/tatanamedzidova/Desktop/ЮСВ КР2 (11).pdf", [29, 30, 32]),
}

DETAIL_TERMS = [
    "slope",
    "площадь кровли",
    "примык",
    "венткан",
    "вентшах",
    "воронк",
    "аэратор",
    "отверст",
    "пробивк",
    "уклон",
]

for name, (path, pages) in DETAIL_PAGES.items():
    doc = fitz.open(path)
    print(f"\n==== {name} ====")
    for page_number in pages:
        text = doc[page_number - 1].get_text("text") or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        print(f"\n-- page {page_number} --")
        for line in lines:
            low = line.lower()
            if any(term in low for term in DETAIL_TERMS):
                print(line[:260])
