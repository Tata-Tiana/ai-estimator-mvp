# GitHub Workflow

Этот файл фиксирует текущее состояние git/GitHub-настройки проекта и рабочие правила, чтобы к ним можно было вернуться без истории чата.

## Репозиторий

- GitHub repository: `https://github.com/Tata-Tiana/ai-estimator-mvp`
- Default branch: `main`
- Active feature branch at time of writing: `feature/ai-project-card`

## Что уже настроено

- Локальный git-репозиторий инициализирован в корне `ai_estimator_mvp`
- Remote `origin` подключен к GitHub-репозиторию
- Автор коммитов настроен локально для этого проекта:
  - `Tatiana Medzhidova`
  - `shugerlife@gmail.com`
- Первый базовый коммит уже создан в `main`
- Ветка `feature/ai-project-card` уже создана и отправлена на GitHub

## Текущая стратегия веток

Используем простую схему:

- `main`
  - только стабильное состояние проекта
  - не использовать для экспериментальной ежедневной работы

- `feature/...`
  - отдельная ветка под отдельную задачу или функциональный блок
  - примеры:
    - `feature/ai-project-card`
    - `feature/pdf-parser`
    - `feature/unikma-integration`
    - `feature/estimate-foundation`
    - `feature/estimate-walls`
    - `feature/estimate-roof`

- `fix/...`
  - ветки для точечных исправлений
  - пример:
    - `fix/project-card-markdown`

- `experiment/...`
  - опционально для коротких исследовательских веток
  - пример:
    - `experiment/material-matching`

## Правило работы

1. `main` хранит чистую и понятную базовую версию проекта.
2. Каждая новая большая задача делается в отдельной ветке.
3. Если задача продолжается несколько дней, не страшно делать много маленьких коммитов в одной feature-ветке.
4. Когда результат становится устойчивым, ветку можно вливать в `main` через Pull Request.

## Базовые команды

### Проверить текущую ветку

```bash
git branch --show-current
```

### Посмотреть состояние файлов

```bash
git status
```

### Переключиться на `main`

```bash
git checkout main
```

### Подтянуть актуальный `main`

```bash
git checkout main
git pull
```

### Создать новую ветку под задачу

```bash
git checkout -b feature/имя-задачи
```

Примеры:

```bash
git checkout -b feature/estimate-foundation
git checkout -b feature/estimate-roof
git checkout -b feature/unikma-integration
```

### Добавить изменения в коммит

```bash
git add .
```

Если нужно аккуратнее, можно добавлять только часть файлов:

```bash
git add experiments/ai_tests
git add docs/git_github_workflow.md
```

### Сделать коммит

```bash
git commit -m "Update AI project card workflow"
```

### Отправить ветку на GitHub

```bash
git push -u origin имя-ветки
```

Пример:

```bash
git push -u origin feature/estimate-roof
```

## Уже существующие ветки

На момент создания файла:

- `main`
- `feature/ai-project-card`

## Уже отправленные ветки на GitHub

На момент создания файла:

- `main`
- `feature/ai-project-card`

## Pull Request

Когда feature-ветка готова, можно открыть Pull Request в `main`.

Для текущей ветки AI-карточки GitHub уже предлагал ссылку вида:

`https://github.com/Tata-Tiana/ai-estimator-mvp/pull/new/feature/ai-project-card`

## Что не должно попадать в git

Это уже закрыто через `.gitignore`, но важно помнить:

- `.env`
- `data/input/`
- `data/output/`
- `.DS_Store`
- `__pycache__/`
- `*.pyc`
- локальные PDF внутри `experiments/pdf_tests/projects/*/input/`
- результаты PDF-парсинга внутри `experiments/pdf_tests/projects/*/output/`
- результаты AI-карточек внутри `experiments/ai_tests/projects/*/output/`

То есть:

- ключи API не коммитим
- локальные PDF и результаты прогонов не коммитим
- в git попадает код, структура, промпты, тестовые скрипты, документация, notes, inputs/expected для расчётных кейсов и README

## Практический ритуал на будущее

Для каждой новой задачи:

1. Перейти в `main`
2. Подтянуть актуальное состояние
3. Создать новую ветку
4. Сделать изменения
5. Проверить `git status`
6. Сделать коммит
7. Запушить ветку

Шаблон:

```bash
git checkout main
git pull
git checkout -b feature/имя-задачи
git add .
git commit -m "Short meaningful message"
git push -u origin feature/имя-задачи
```

## Комментарий по проекту

Этот проект развивается поэтапно:

- эксперименты по PDF-парсингу
- AI-карточка проекта
- интеграция с УНИКМА
- логика расчета разделов сметы

Поэтому ветки лучше вести по смысловым блокам, а не смешивать много направлений в одной ветке.
