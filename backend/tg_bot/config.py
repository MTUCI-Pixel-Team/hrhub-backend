import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота из переменной окружения или значение
TOKEN = os.environ.get("TG_BOT_TOKEN")
