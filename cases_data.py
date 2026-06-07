"""Данные кейсов для публичной части сайта."""

CASES = [
    {
        "id": 1,
        "slug": "telegram-bot",
        "title": "Разработка Telegram-бота для бизнеса",
        "short_description": (
            "RAG-ассистент в Telegram: ответы на основе базы знаний, "
            "кеширование запросов и логирование диалогов. Развёрнут на VPS 24/7."
        ),
        "image": "case1.svg",
        "github_url": "https://github.com/Nvtrap/PEcf09",
        "telegram_url": "https://t.me/LargyBBot",
        "telegram_bot_name": "@LargyBBot",
        "detail": {
            "challenge": (
                "Бизнесу нужен канал поддержки в Telegram, который отвечает на типовые "
                "вопросы по документации компании без участия оператора и без долгого "
                "ожидания ответа."
            ),
            "solution": (
                "Разработан Telegram-бот с технологией RAG (Retrieval-Augmented Generation): "
                "семантический поиск по базе знаний в ChromaDB, генерация ответов через OpenAI, "
                "кеширование повторных запросов и журнал всех диалогов в SQLite. "
                "Бот развёрнут на VPS (Timeweb) и работает как systemd-служба."
            ),
            "results": [
                "Ускорение работы технической поддержки в 5 раз",
                "Среднее время ответа уменьшено вдвое за счёт кеширования",
                "Круглосуточные ответы в Telegram без участия менеджера",
                "Экспорт логов и статистика (/stats, /logs) для анализа обращений",
            ],
            "technologies": [
                "Python",
                "Telegram Bot API",
                "RAG",
                "ChromaDB",
                "OpenAI",
                "SQLite",
                "systemd",
            ],
        },
    },
    {
        "id": 2,
        "slug": "fine-tuning-lora",
        "title": "Fine-tuning русской модели с LoRA",
        "short_description": (
            "Дообучение ruGPT3small на русском датасете вопросов по Python: "
            "LoRA-адаптер, HuggingFace, обучение на CPU."
        ),
        "image": "case6.svg",
        "github_url": "https://github.com/Nvtrap/PEcj10",
        "detail": {
            "challenge": (
                "Нужен компактный русскоязычный ассистент по Python, адаптированный "
                "под учебный формат вопросов и ответов, без полного переобучения большой модели."
            ),
            "solution": (
                "Реализован пайплайн fine-tuning на базе sberbank-ai/rugpt3small_based_on_gpt2 "
                "с технологией LoRA (PEFT): подготовка датасета instruction/output, обучение "
                "адаптера на 87 примерах, сохранение весов и запуск чата через transformers."
            ),
            "results": [
                "Модель дообучена на русском датасете за 3 эпохи",
                "LoRA-адаптер занимает ~10 МБ вместо полной модели",
                "Пайплайн работает на CPU без GPU",
                "Проект опубликован на GitHub с инструкцией запуска",
            ],
            "technologies": [
                "Python",
                "PyTorch",
                "Transformers",
                "PEFT",
                "LoRA",
                "HuggingFace",
            ],
        },
    },
    {
        "id": 3,
        "slug": "faq-assistant",
        "title": "FAQ-ассистент",
        "short_description": (
            "Веб-ассистент с RAG (FAISS + OpenAI): ответы на частые вопросы "
            "клиентов на основе базы знаний компании."
        ),
        "image": "case3.svg",
        "github_url": "https://github.com/Nvtrap/PEcj11",
        "detail": {
            "challenge": (
                "Клиенты задают одни и те же вопросы: сроки, условия, тарифы. "
                "Менеджеры тратят время на повторяющиеся ответы."
            ),
            "solution": (
                "Разработан FAQ-ассистент на сайте: пользователь задаёт вопрос в чат-виджете, "
                "backend ищет релевантные фрагменты в базе знаний через FAISS и формирует "
                "понятный ответ на русском языке с помощью OpenAI."
            ),
            "results": [
                "Снижение нагрузки на службу поддержки на 25%",
                "Мгновенные ответы на типовые вопросы 24/7",
                "Единая база знаний: FAQ JSON и документы .txt",
            ],
            "technologies": [
                "Python",
                "FastAPI",
                "FAISS",
                "OpenAI",
                "RAG",
                "Flask",
            ],
        },
    },
]


def get_case_by_slug(slug: str) -> dict | None:
    """Возвращает кейс по slug или None."""
    for case in CASES:
        if case["slug"] == slug:
            return case
    return None
