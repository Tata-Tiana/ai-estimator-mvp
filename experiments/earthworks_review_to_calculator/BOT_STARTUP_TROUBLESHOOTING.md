# Telegram-бот не запускается после правок кода — что проверять

Читай это ПЕРВЫМ, до того как менять код или гонять `launchctl` вслепую. Написано после реального
случая 2026-08-27: код был исправен, а бот всё равно "не запускался" — причина оказалась не в коде.

## 0. Сначала пойми, что вообще значит "не запускается"

`telegram_bot.py` — production-процесс, управляется через launchd (`~/Library/LaunchAgents/
com.aiestimator.earthworks.telegrambot.plist`, `RunAtLoad` + `KeepAlive`, то есть он должен сам
перезапускаться при падении). Если он "не отвечает" в Telegram, это почти всегда одно из трёх, не
обязательно "код сломан":

1. Штатный launchd-сервис не загружен вообще (см. п.1).
2. Одновременно работают ДВЕ копии бота на одном токене (см. п.2) — Telegram даёт
   `Conflict: terminated by other getUpdates request`, и обе копии перестают отвечать.
3. Реальная синтаксическая/импортная ошибка в коде (см. п.3) — это на самом деле редкий случай,
   проверяется быстрее всего, но чаще всего НЕ он.

## 1. Проверить, загружен ли штатный launchd-сервис

```bash
launchctl print gui/$(id -u)/com.aiestimator.earthworks.telegrambot
```

- `Could not find service` → сервис не загружен вообще. Загрузить:
  `launchctl load ~/Library/LaunchAgents/com.aiestimator.earthworks.telegrambot.plist`
- Если загружен, но `last exit code` не "(never exited)" — смотри `state`/exit code, ищи причину в
  логах (п.3).

## 2. Проверить, нет ли второй копии бота

Частый сценарий: во время правок кто-то (ты, Кодекс, или прошлая сессия Клода) запустил
`telegram_bot.py` вручную в терминале для теста и забыл убить процесс. Через launchd он потом
запускается второй раз — два поллера на одном токене конфликтуют, и обе копии выглядят "не
работающими".

```bash
ps aux | grep telegram_bot.py | grep -v grep
```

Если строк больше одной — не гадай, какая "правильная". Убей все процессы, чьим родителем НЕ
является launchd (родитель launchd-процесса — `launchd`/`1`; ad hoc процесс, запущенный из
терминала или другим агентом, будет висеть на родителе вроде вашего шелла, VS Code, Кодекса и
т.п. — проверь `ps -o pid,ppid,command -p <pid>`), затем перезагрузи штатный сервис:

```bash
kill <ad_hoc_pid>
launchctl load ~/Library/LaunchAgents/com.aiestimator.earthworks.telegrambot.plist
# если уже был загружен и просто завис — вместо load:
launchctl kickstart -k gui/$(id -u)/com.aiestimator.earthworks.telegrambot
```

**Никогда не гоняй `telegram_bot.py` напрямую в терминале дольше пары секунд теста** — это ровно
тот сценарий, что уже один раз всё сломал. Для быстрой проверки синтаксиса используй п.3, не полный
запуск с поллингом.

## 3. Проверить сам код (быстро, без реального запуска)

```bash
cd /Users/tatanamedzidova/Desktop/ai_estimator/ai_estimator_mvp
source .venv/bin/activate
python3 -m py_compile experiments/earthworks_review_to_calculator/telegram_bot.py   # синтаксис
python3 -c "import sys; sys.path.insert(0,'experiments/earthworks_review_to_calculator'); import telegram_bot"  # импорты
```

Оба падают без сети/токена — если ошибка, она про реальный синтаксис/опечатку/недостающий импорт,
а не про сеть. Если оба проходят чисто — код не виноват, возвращайся к п.1-2.

**ВАЖНО про venv:** `ps` иногда показывает путь к системному Python-фреймворку даже когда процесс
реально работает из `.venv` (macOS venv launcher так устроен). Не делай вывод "venv не тот" только
по `ps`-строке — проверяй `lsof -p <pid> | grep site-packages` (должно указывать на `.venv/lib/...`)
или переменную окружения `__PYVENV_LAUNCHER__` процесса.

## 4. Где смотреть логи

- `experiments/earthworks_review_to_calculator/data/telegram_logs/runtime/telegram_bot_launchctl.out.log`
  — stdout штатного launchd-процесса ("Bot started. Polling..." при успехе).
- `.../telegram_bot_launchctl.err.log` — stderr, полные traceback'и. **Смотри именно КОНЕЦ файла
  по времени** (`tail`), не первую попавшуюся ошибку — файл копится годами, старые ReadTimeout'ы
  от сети это нормально и не признак поломки (у бота есть свой retry-луп на них).
- Если видишь `telegram_bot_supervisor.log` с частыми повторами "start" — это признак реального
  crash-loop, а не сетевого шума.

## 5. После любого фикса — обязательно проверь, что PID стабилен

Одного "Bot started" в логе недостаточно — процесс мог тут же упасть и это просто последняя строка
перед смертью. Подожди 5-10 секунд и перепроверь:

```bash
launchctl print gui/$(id -u)/com.aiestimator.earthworks.telegrambot | grep -E "pid|state|last exit"
```

`state = running` и стабильный `pid` (не сменился) — можно считать поднятым.
