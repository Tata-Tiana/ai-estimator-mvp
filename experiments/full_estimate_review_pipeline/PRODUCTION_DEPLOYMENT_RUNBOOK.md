# Памятка по переносу калькулятора на сервер

Дата фиксации: 2026-09-24. Последнее обновление: 2026-09-29.

Документ фиксирует договорённости с директором, результаты первичного обследования
сервера и безопасную последовательность будущего развёртывания. Это памятка и
чек-лист, а не свидетельство выполненного деплоя.

## Текущий результат

На 2026-09-24 выполнено только чтение состояния сервера. Файлы, пакеты, сервисы,
firewall и настройки SSH на сервере не изменялись. На 2026-09-29 завершена локальная
подготовка релиза; перенос на сервер ещё не выполнялся.

Подтверждено:

- SSH-доступ работает существующим ключом `~/.ssh/id_ed25519` после его разблокировки
  через `ssh-add`. Email в ключе является комментарием, а не логином сервера.
- Сервер работает на Ubuntu 22.04.5 LTS.
- Пользователь `calc` уже создан; приложение должно жить в `/home/calc/`.
- Доступны Python 3.10, `python3-venv` и Git.
- Docker на сервере не установлен. Устанавливать его для этого приложения не нужно:
  согласован отдельный Python `venv` и отдельный `systemd`-сервис.
- На сервере уже работают `snab_bot` и `photo_bot`; их файлы и сервисы не трогать.
- На момент обследования свободно около 9,8 ГБ диска, оперативной памяти около
  957 МиБ, swap отсутствует. Поэтому нельзя копировать локальные логи, загрузки,
  тестовые PDF и весь рабочий каталог без фильтрации.
- `calc.service` пока не существует.
- Локальная копия калькулятора сейчас запущена на Mac через LaunchAgent
  `com.aiestimator.earthworks.telegrambot`. Перед первым запуском на сервере её
  обязательно остановить.

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

8. Telegram API с сервера доступен только через SOCKS5-прокси. Endpoint, логин и
   пароль хранить как секреты; в Git и в эту памятку их не записывать.
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

### 2. Добавить поддержку Telegram SOCKS5

`telegram_bot.py` теперь настраивает отдельный SOCKS5 только для Telegram. Выполнено:

- добавить `PySocks` в production-зависимости;
- читать отдельные переменные `TELEGRAM_PROXY_HOST`, `TELEGRAM_PROXY_PORT`,
  `TELEGRAM_PROXY_USERNAME`, `TELEGRAM_PROXY_PASSWORD`;
- настроить proxy в `telebot.apihelper` до создания `TeleBot`;
- применять прокси только к Telegram, а не задавать общий `HTTPS_PROXY`, иначе через
  него могут случайно пойти Google API и другие запросы;
- не печатать URL с логином и паролем в stdout, journal и диагностические экспорты;
- добавлены тесты разбора настроек без вывода реквизитов;
- smoke-проверка через серверный прокси остаётся серверным этапом C.

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

- [x] Реализована и протестирована локальная поддержка SOCKS5.
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
    --proxy "socks5h://${TELEGRAM_PROXY_HOST}:${TELEGRAM_PROXY_PORT}" \
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

## Следующая практическая точка

Локальные задачи выполнены:

1. поддержка SOCKS5 только для Telegram;
2. production manifest + `requirements-prod.txt`;
3. завершение Google OAuth и локальный end-to-end smoke-test семи разделов.

Следующая точка: создать release commit/tag, затем провести перенос строго по этапам
B-F и зафиксировать фактические команды, release tag и результаты smoke-test в
отдельном отчёте деплоя.
