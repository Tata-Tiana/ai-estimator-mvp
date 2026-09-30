# Памятка по переносу калькулятора на сервер

Дата фиксации: 2026-09-24. Последнее обновление: 2026-09-29.

Документ фиксирует договорённости с директором, результаты обследования сервера,
безопасную последовательность и фактический результат развёртывания.

## Текущий результат

На 2026-09-24 выполнено первичное чтение состояния сервера. На 2026-09-29 завершена
локальная подготовка релиза и выполнена установка приложения на сервер. Локальный
poller остановлен, серверный `calc.service` запущен через HTTP-прокси.

Подтверждено:

- SSH-доступ работает существующим ключом `~/.ssh/id_ed25519` после его разблокировки
  через `ssh-add`. Email в ключе является комментарием, а не логином сервера.
- Сервер работает на Ubuntu 22.04.5 LTS.
- Пользователь `calc` уже создан; приложение должно жить в `/home/calc/`.
- Доступны Python 3.10 и Git; системный пакет `python3-venv` отсутствует.
- Docker на сервере не установлен. Устанавливать его для этого приложения не нужно:
  согласован отдельный Python `venv` и отдельный `systemd`-сервис.
- На сервере уже работают `snab_bot` и `photo_bot`; их файлы и сервисы не трогать.
- На момент обследования свободно около 9,8 ГБ диска, оперативной памяти около
  957 МиБ, swap отсутствует. Поэтому нельзя копировать локальные логи, загрузки,
  тестовые PDF и весь рабочий каталог без фильтрации.
- `calc.service` установлен, включён (`enabled`) и работает (`active`) от `calc`;
  `NRestarts=0`, ошибок и конфликтов polling в журнале нет.
- Локальный LaunchAgent `com.aiestimator.earthworks.telegrambot` остановлен перед
  первым запуском серверного экземпляра.

Фактический результат установки 2026-09-29:

- release commit `1dcefa9`, tag `first-part-production-2026-09-29`, обновление
  HTTP-прокси `cf80c93`;
- приложение установлено в `/home/calc/ai-estimator-mvp`, владелец `calc:calc`;
- секреты и OAuth-файлы установлены в `/home/calc/.config/ai-estimator/` с правами
  `600`; временные копии из `/tmp` удалены;
- зависимости установлены только в проектный `.venv`, без `apt` и без изменения
  глобальных Python-пакетов;
- Google на сервере читает все 120 рабочих цен без предупреждений;
- серверный smoke-test собрал семь разделов и итоговый Excel с 2631 формулой и
  печатной областью `A:I`;
- `snab_bot` и `photo_bot` остались активны и не перезапускались;
- техподдержка подтвердила, что для Telegram из РФ нужно использовать HTTP или MTP;
  выданный HTTP endpoint успешно прошёл серверный `curl getMe`;
- локальный LaunchAgent остановлен; `calc.service` является единственным poller.

Google OAuth:

- используется существующий проект `AI Estimator MVP` в аккаунте директора;
- приложение переведено из `Testing` в `In production`;
- выбран обычный OAuth директора, а не service account: личный Gmail не даёт
  Shared Drive, а сервисный аккаунт не должен становиться владельцем рабочих смет;
- сохранены scopes `drive.file` и `spreadsheets`;
- создан OAuth client типа `Desktop app` именно в проекте `AI Estimator MVP`;
- выпущен новый production-токен под Gmail директора;
- в Drive директора создана новая приватная рабочая папка и перенесён актуальный
  `price_registry_filled_v4.xlsx` (221 строка листа, 120 рабочих строк с `price_code`);
- локально проверены чтение прайса, создание приватной Google-таблицы, обратное
  скачивание в `.xlsx` и удаление тестового файла;
- старый тестовый `token.json` в продакшн не переносить.

## Жёсткие правила директора

1. Проект размещать только внутри `/home/calc/`; в `/root` ничего не класть.
2. Процесс должен работать от `User=calc` и `Group=calc`.
3. Python-зависимости устанавливать только в отдельный `venv` проекта. Глобальный
   `pip install` и обновление системного Python запрещены.
4. Не трогать `/root/Snab_Bot`, `/root/photobot`, `snab_bot.service` и
   `photo_bot.service`.
5. Перед любым `apt install`, изменением firewall или SSH предварительно написать
   директору и получить разрешение.
6. Сервер не перезагружать. После установки проверить только
   `systemctl is-enabled calc`; контрольную перезагрузку директор выполнит сам.
7. Сервис назвать `calc.service` и настроить:

   ```ini
   Restart=on-failure
   RestartSec=10
   ```

8. Telegram API с сервера доступен только через прокси. Первоначально был указан
   SOCKS5, но техподдержка подтвердила использование HTTP или MTP для Telegram из РФ.
   Рабочий HTTP endpoint проверен через `getMe`. Endpoint, логин и пароль хранить как
   секреты; в Git и в эту памятку их не записывать.
9. До первого запуска бота на сервере остановить локальную копию, включая любой
   ручной тест на сервере. Одновременно должен работать только один poller с данным
   Telegram-токеном.
10. После успешного запуска директор уберёт root-доступ и оставит доступ
    пользователю `calc`.

## Выбранная схема

- Исходники поставляются из отдельного приватного production-репозитория либо из
  специально подготовленной deploy-ветки. Рабочий каталог разработчика целиком на
  сервер не копируется.
- Размещение: `/home/calc/ai-estimator-mvp`.
- Виртуальное окружение: `/home/calc/ai-estimator-mvp/.venv`.
- Секреты: `/home/calc/.config/ai-estimator/calc.env` и
  `/home/calc/.config/ai-estimator/google/`.
- Постоянные данные бота остаются внутри каталога приложения только там, где этого
  сейчас требует код. Для них заранее создаются каталоги с владельцем `calc`.
- Управление процессом выполняет только `systemd`; `tmux`, `screen`, `nohup` и
  параллельный ручной процесс не используются.
- Логи процесса читаются через `journalctl`. Нельзя направлять бесконечный stdout в
  обычный файл без ротации: локальная история уже показала рост такого лога до
  1,8 ГБ.

## Локальная подготовка перед переносом

### 1. Собрать production-пакет

Локальный рабочий каталог занимает около 3,2 ГБ главным образом из-за игнорируемых
логов и загрузок. В Git отслеживается около 68 МБ, но там всё равно много отчётов,
старых экспериментов и тестовых проектов.

Нельзя делать `scp -r` текущего репозитория. На 2026-09-29 выполнено:

1. Проследить runtime-зависимости семи готовых разделов от `telegram_bot.py` до всех
   калькуляторов, шаблонов и справочников.
2. Сформировать явный production manifest.
3. Исключить отчёты разработки, реальные исходные PDF, локальные jobs, логи,
   скриншоты, тестовые результаты и все токены.
4. Создать отдельный `requirements-prod.txt` с зафиксированными версиями.
5. Проверить собранный пакет в чистом временном каталоге.
6. Поставлять только подтверждённый commit/tag, а не грязное рабочее дерево.

Созданы `deploy/production_manifest.txt`, `deploy/build_production_package.py` и
`requirements-prod.txt`. Проверенный архив содержит 116 runtime-файлов, занимает
около 664 КБ и не содержит `.env`, OAuth JSON, токены, реальные PDF, jobs и логи.
Из чистой распакованной копии успешно собраны семь разделов и итоговый Excel.
Наличие Linux wheels для всего списка зависимостей отдельно проверено под серверный
Python 3.10; несовместимый локальный пин Pillow заменён на совместимый `12.2.0`.

### 2. Добавить поддержку Telegram-прокси

После commit `d24d3e2` Telegram-транспорт переведён на тот же стек, что у двух
действующих серверных ботов. Выполнено:

- заменить `pyTelegramBotAPI/PySocks` на `python-telegram-bot[socks]==22.7`;
- читать отдельные переменные `TELEGRAM_PROXY_SCHEME`, `TELEGRAM_PROXY_HOST`,
  `TELEGRAM_PROXY_PORT`, `TELEGRAM_PROXY_USERNAME`, `TELEGRAM_PROXY_PASSWORD`;
- создать один штатный `HTTPXRequest` для Bot API и `getUpdates`, как в двух
  действующих ботах;
- выполнять синхронные обработчики в рабочих потоках, не блокируя asyncio polling;
- применять прокси только к Telegram, а не задавать общий `HTTPS_PROXY`, иначе через
  него могут случайно пойти Google API и другие запросы;
- подавить HTTPX request-логи и фильтровать токен/полный proxy URL;
- добавлены тесты транспорта, файлов и настроек прокси; основной набор: 20 passed;
- smoke-проверка через серверный прокси остаётся серверным этапом C.

Повторная проверка SOCKS5 29.09.2026:

- `snab_bot` и `photo_bot` проверены только на чтение; оба действительно работают
  через один SOCKS5 endpoint и `HTTPX/socksio`;
- одиночный `getMe` для `calc` через тот же endpoint вернул `ok=true`;
- при запуске постоянного polling `calc` получил `socksio ProtocolError: Malformed reply`;
- эксперимент откачен из резервной копии. Текущий production-режим `calc` — HTTP,
  `active`, `enabled`, `NRestarts=0`; два других бота не менялись и не перезапускались.

После решения директора использовать SOCKS5 выполнена полноценная PTB-миграция.
Код установлен и запущен на HTTP: `Application started`, `NRestarts=0`. SOCKS URL и
версии библиотек побайтно совпадают с существующими ботами, однако отдельный PTB
`getMe` всё равно получает `Malformed reply` во время SOCKS-аутентификации.

На endpoint уже установлены три TCP-соединения: `photo_bot.service`,
`snab_bot.service` и отдельный `/root/photobot/bot.py` из `cron.service` (PID 578).
Этот процесс не изменялся. До подтверждения лимита соединений или выдачи отдельного
endpoint `calc` временно остаётся на HTTP.

Повторная низкоуровневая проверка после сообщения об отсутствии лимита показала:
TCP к endpoint устанавливается, но на SOCKS5 greeting `05 01 02` прокси не возвращает
ни одного байта; через 10 секунд наступает timeout. Стандартный `curl` через SOCKS5
завершается с кодом 28, а тот же endpoint как HTTP proxy возвращает ответ Telegram
примерно за две секунды. Это происходит до проверки credentials и запроса Telegram.

Итоговый ответ поставщика: endpoint `82.117.86.224:63475` указан правильно, новые
сессии разрешены и HTTP-only режим не включён, однако SOCKS5 поставщика не работает
с Telegram при исходящем подключении из РФ. Порт не заблокирован: TCP connect с
production-сервера проходит. Поэтому штатный production-режим `calc` — HTTP proxy;
SOCKS5 не включать без другого endpoint или исходящего узла вне РФ.

Последующая проверка выявила недоступность endpoint и в HTTP-режиме: новые запросы
к Telegram, Google и `example.com` завершаются timeout; то же самое воспроизводится
с Mac. Старые серверные TCP-соединения остаются `ESTAB`. Поэтому до ответа
поставщика одного `systemctl is-active calc` недостаточно: необходимо подтверждать
реальный ответ `/start` или наличие рабочего polling-соединения.

На последующем скриншоте техподдержка проверяла порт `64357`, а не выданный и ранее
подтверждённый `63475`. Credentials на скриншоте скрыты. Проверка `64357` с текущими
credentials не дала рабочего CONNECT: curl 97 / SOCKS reply code 2. Production-
конфигурацию не менять, пока поставщик не подтвердит полный набор endpoint и
принадлежность тестовых credentials той же учётной записи.

Финальное рабочее состояние 30.09.2026: для `calc` выдан отдельный новый прокси.
SOCKS5 нового прокси работает для обычных сайтов, но Telegram с российского сервера
не пропускает; HTTP endpoint прошёл пять `getMe` из пяти. Production переключён на
новый HTTP endpoint с backup
`/home/calc/deploy-backups/proxy_switch_20260930_124542`. `calc.service` имеет
`active/running`, `NRestarts=0` и установленное proxy-соединение.

### 3. Google OAuth

Выполнено 2026-09-29:

1. В `Data Access` сохранены:
   - `https://www.googleapis.com/auth/drive.file`;
   - `https://www.googleapis.com/auth/spreadsheets`.
2. Для `spreadsheets` сохранить подготовленное обоснование. Статус
   `Approval required` допустим: OAuth использует только один аккаунт директора.
3. Проверить, что включены Google Drive API и Google Sheets API.
4. Использовать OAuth client типа `Desktop app`.
5. После перехода в production выпущен новый `token.json` под Gmail директора.
6. Локально проверены чтение прайса, создание Google-таблицы и обратное скачивание.
7. Осталось передать `credentials.json` и новый `token.json` на сервер не через Git и выдать
   им права `600`, владельца `calc`.

### 4. Закрыть production-настройки

Директор подтвердил, что бот должен быть открытым. Поэтому планируется
`ALLOW_ALL_USERS=true`; административные команды всё равно должны оставаться только
для `TELEGRAM_ADMIN_CHAT_IDS`.

Нужно отдельно подтвердить режим публикации review-таблиц. Сейчас код использует
`anyone_writer`: любой человек со ссылкой может редактировать таблицу. Это существующее
поведение, но перед запуском оно должно быть осознанно принято либо заменено более
узким доступом.

## Секреты и environment

Секретный файл не входит в репозиторий:

```text
/home/calc/.config/ai-estimator/calc.env
```

Ожидаемый состав без реальных значений:

```dotenv
TELEGRAM_BOT_TOKEN=
ALLOW_ALL_USERS=true
TELEGRAM_ADMIN_CHAT_IDS=

TELEGRAM_PROXY_SCHEME=http
TELEGRAM_PROXY_HOST=
TELEGRAM_PROXY_PORT=
TELEGRAM_PROXY_USERNAME=
TELEGRAM_PROXY_PASSWORD=

GOOGLE_OAUTH_CREDENTIALS_PATH=/home/calc/.config/ai-estimator/google/credentials.json
GOOGLE_TOKEN_PATH=/home/calc/.config/ai-estimator/google/token.json
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_PRICE_REGISTRY_SPREADSHEET_ID=
GOOGLE_PRICE_REGISTRY_SHEET_NAME=price_registry
```

Права:

```bash
chmod 700 /home/calc/.config/ai-estimator
chmod 700 /home/calc/.config/ai-estimator/google
chmod 600 /home/calc/.config/ai-estimator/calc.env
chmod 600 /home/calc/.config/ai-estimator/google/credentials.json
chmod 600 /home/calc/.config/ai-estimator/google/token.json
chown -R calc:calc /home/calc/.config/ai-estimator
```

Пароли, токены, OAuth JSON и приватный SSH-ключ не вставлять в задачи, отчёты,
коммиты, service-файл или команды, сохраняемые в shell history.

## Пошаговый перенос

### Этап A. Локальная подготовка

- [x] Реализована и протестирована локальная поддержка HTTP и SOCKS5.
- [x] Создан и проверен production manifest.
- [x] Создан `requirements-prod.txt`.
- [x] Все тесты семи разделов проходят из чистого production-пакета.
- [x] Google OAuth завершён и получен новый production-токен.
- [x] Проверено прямое создание итогового `.xlsx`: Google Sheets используется только
      для промежуточной проверки себестоимости, а не конвертируется в итоговую смету.
- [x] В итоговом `.xlsx` настроена печатная область `A:I`; серая себестоимость и правые
      подсказки не попадают в клиентскую печать.
- [ ] Зафиксирован release commit и tag.
- [ ] Секреты отсутствуют в Git и проверены через `git status`/`git grep`.
- [ ] Подготовлен точный rollback commit/tag.

### Этап B. Серверный preflight без изменений

Перед переносом повторно проверить:

```bash
id calc
python3 --version
git --version
df -h /
free -h
systemctl is-active snab_bot
systemctl is-active photo_bot
systemctl status calc --no-pager
```

Ожидаемо последняя команда до установки сообщает, что `calc.service` отсутствует.

### Этап C. Проверка прокси через curl

Сначала создать закрытый `calc.env`, затем выполнить проверку от пользователя `calc`.
Пароль при этом остаётся в файле и не попадает в историю команд:

```bash
sudo -u calc bash -lc '
  set -a
  source /home/calc/.config/ai-estimator/calc.env
  set +a
  curl --fail --silent --show-error \
    --proxy "${TELEGRAM_PROXY_SCHEME}://${TELEGRAM_PROXY_HOST}:${TELEGRAM_PROXY_PORT}" \
    --proxy-user "${TELEGRAM_PROXY_USERNAME}:${TELEGRAM_PROXY_PASSWORD}" \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
'
```

Успешный ответ должен содержать `"ok":true`. Эта команда не запускает polling и не
конфликтует с работающей локальной копией.

### Этап D. Установка приложения

Команды уточняются после создания production-репозитория. Общая схема:

```bash
install -d -o calc -g calc -m 750 /home/calc/ai-estimator-mvp
sudo -u calc git clone <PRIVATE_PRODUCTION_REPOSITORY> /home/calc/ai-estimator-mvp
sudo -u calc python3 -m venv /home/calc/ai-estimator-mvp/.venv
sudo -u calc /home/calc/ai-estimator-mvp/.venv/bin/python -m pip install \
  -r /home/calc/ai-estimator-mvp/requirements-prod.txt
```

Если для этого неожиданно потребуется `apt`, остановиться и сначала написать
директору. Ничего не устанавливать самостоятельно.

До запуска polling разрешены проверки, не обращающиеся к Telegram:

```bash
sudo -u calc /home/calc/ai-estimator-mvp/.venv/bin/python -m compileall -q \
  /home/calc/ai-estimator-mvp
```

Также до первого запуска проверить локально подготовленными fixtures сборку семи
разделов и Google smoke-test без создания второго Telegram poller.

### Этап E. `calc.service`

Целевой service-файл:

```ini
[Unit]
Description=AI Estimator Telegram bot
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=calc
Group=calc
WorkingDirectory=/home/calc/ai-estimator-mvp
EnvironmentFile=/home/calc/.config/ai-estimator/calc.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/calc/ai-estimator-mvp/.venv/bin/python -u /home/calc/ai-estimator-mvp/experiments/earthworks_review_to_calculator/telegram_bot.py
Restart=on-failure
RestartSec=10
TimeoutStopSec=30
UMask=0077
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Файл устанавливается как `/etc/systemd/system/calc.service`. После установки:

```bash
systemctl daemon-reload
systemctl enable calc
systemctl is-enabled calc
```

Ожидаемый результат последней команды: `enabled`. Сервер не перезагружать.

### Этап F. Переключение единственного poller

Этот этап выполнять только после успешных preflight, proxy, импортов и Google-тестов.

1. На Mac остановить LaunchAgent:

   ```bash
   launchctl bootout gui/$(id -u)/com.aiestimator.earthworks.telegrambot
   ```

2. Убедиться, что локальный сервис действительно остановлен:

   ```bash
   launchctl print gui/$(id -u)/com.aiestimator.earthworks.telegrambot
   ```

   Ожидается сообщение, что сервис не найден.

3. Только после этого запустить серверную копию:

   ```bash
   systemctl start calc
   systemctl status calc --no-pager
   journalctl -u calc -n 100 --no-pager
   ```

4. Проверить команды бота в Telegram: `/start`, `/help`, затем отдельным тестовым
   проектом полный путь JSON → review workbook → `/build`.
5. Убедиться, что промежуточная таблица создаётся в аккаунте директора, прайс читается,
   а итоговый Excel формируется напрямую и возвращается пользователю.
6. Открыть итоговый `.xlsx` в Excel, изменить одно тестовое входное значение и проверить
   пересчёт обеих частей; в предварительном просмотре печати должны присутствовать только `A:I`.
7. Ещё раз выполнить `systemctl is-enabled calc`. Сервер не перезагружать; сообщить
   директору, что можно выполнить контрольную перезагрузку.

## Проверки после запуска

```bash
systemctl is-active calc
systemctl is-enabled calc
systemctl status calc --no-pager
journalctl -u calc --since "15 minutes ago" --no-pager
df -h /
free -h
systemctl is-active snab_bot
systemctl is-active photo_bot
```

Проверить отдельно:

- в журнале нет proxy credentials, Telegram-токена и Google refresh token;
- сервис работает как `calc`, а не `root`;
- нет второго процесса калькулятора;
- `snab_bot` и `photo_bot` не перезапускались;
- приложение пишет только в разрешённые каталоги `/home/calc/`;
- после временной сетевой ошибки действует `Restart=on-failure` с задержкой 10 секунд;
- диск не растёт из-за необрезаемых логов и загруженных проектов.

## Откат

Если серверная копия не проходит проверку:

```bash
systemctl stop calc
systemctl status calc --no-pager
```

После полной остановки сервера можно временно вернуть локальную копию:

```bash
launchctl bootstrap gui/$(id -u) \
  "$HOME/Library/LaunchAgents/com.aiestimator.earthworks.telegrambot.plist"
```

Никогда не запускать локальную и серверную копии одновременно. Код на сервере
откатывать на заранее записанный release tag/commit, затем повторять проверки от
этапа D. Системные пакеты, firewall, SSH и чужие сервисы при откате не менять.

## Что не делать

- Не копировать локальную `.venv`: окружение создаётся заново на Ubuntu.
- Не переносить локальные `data/telegram_logs`, uploads и старые jobs.
- Не использовать старый testing-токен Google.
- Не помещать секреты в GitHub Actions variables без отдельной необходимости.
- Не запускать `pip` через `sudo`.
- Не делать `apt upgrade`, `ufw`, изменения `sshd_config` или reboot.
- Не выполнять `systemctl restart` для чужих ботов.
- Не считать успешный `curl getMe` полноценным тестом приложения.
- Не запускать ручной `python telegram_bot.py`, пока локальный poller активен.

## Текущий итог

Локальные задачи выполнены:

1. PTB/HTTPX-транспорт с поддержкой HTTP/SOCKS5 только для Telegram;
2. production manifest + `requirements-prod.txt`;
3. завершение Google OAuth и локальный end-to-end smoke-test семи разделов.

Перенос по этапам B-F выполнен. Осталась пользовательская проверка в Telegram:
`/start`, загрузка проекта, JSON → Google Sheet и `/build` → итоговый `.xlsx`.
