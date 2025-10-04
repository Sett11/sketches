"""
Telegram бот для уведомлений о работе парсера КАДР Арбитр
Функции:
- Подписка на уведомления (/start)
- Получение уведомлений от парсера через JSON файл
- Отправка сообщений всем подписчикам
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
LOG_DIR = Path(os.getenv('LOGS_DIR', '/app/data/logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
DB_PATH = Path(os.getenv('DB_PATH', '/app/data/state/database.db'))
NOTIFICATION_FILE = Path(os.getenv('STATE_DIR', '/app/data/state')) / 'notifications.json'


class KadrBot:
    """Telegram бот для уведомлений"""
    
    def __init__(self, token: str):
        if not token or token == 'YOUR_BOT_TOKEN_HERE':
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен! Укажите токен в .env файле")
        
        self.token = token
        self.app = Application.builder().token(token).build()
        self.last_notification_timestamp = None
        
        # SQLite для подписчиков (используем ту же БД что и парсер)
        from database import Database
        self.db = Database(DB_PATH)
        
        # Регистрация обработчиков команд
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start - подписка на уведомления"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Добавляем подписчика в БД
        self.db.add_subscriber(
            chat_id=chat_id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )
        
        welcome_message = (
            f"👋 Привет, {user.first_name}!\n\n"
            f"Вы подписаны на уведомления от парсера КАДР Арбитр.\n\n"
            f"Вы будете получать:\n"
            f"• Уведомления о старте парсера\n"
            f"• Информацию о прогрессе\n"
            f"• Финальную статистику\n"
            f"• Сообщения об ошибках\n\n"
            f"Команды:\n"
            f"/help - помощь\n"
            f"/status - текущий статус"
        )
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Новый подписчик: {user.username} (ID: {chat_id})")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📚 *Помощь по боту КАДР Арбитр*\n\n"
            "*Команды:*\n"
            "/start - подписаться на уведомления\n"
            "/help - показать эту справку\n"
            "/status - показать текущий статус\n\n"
            "*Уведомления:*\n"
            "Бот автоматически отправляет уведомления о работе парсера.\n\n"
            "*Вопросы?*\n"
            "Обратитесь к администратору системы."
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status - показать статистику"""
        try:
            stats = self.db.get_statistics()
            
            status_message = (
                f"📊 *Статистика базы данных:*\n\n"
                f"📅 Обработано дат: {stats['processed_dates']}\n"
                f"📄 Скачано файлов: {stats['downloaded_files']}\n"
                f"💾 Общий размер: {stats['total_size_mb']} MB\n"
                f"👥 Подписчиков: {stats['bot_subscribers']}"
            )
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text("Ошибка при получении статистики")
    
    async def check_notifications(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Проверка новых уведомлений от парсера
        Вызывается периодически (каждые 2 секунды)
        """
        try:
            # Проверяем наличие файла с уведомлениями
            if not NOTIFICATION_FILE.exists():
                return
            
            # Читаем уведомление
            with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            timestamp = notification.get('timestamp')
            message = notification.get('message')
            
            # Проверяем, не отправляли ли мы уже это уведомление
            if timestamp == self.last_notification_timestamp:
                return
            
            # Отправляем уведомление всем подписчикам
            subscribers = self.db.get_all_subscribers()
            
            if not subscribers:
                logger.warning("Нет подписчиков для отправки уведомления")
            
            sent_count = 0
            for chat_id in subscribers:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=None
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
            
            logger.info(f"Уведомление отправлено {sent_count} подписчикам: {message[:50]}...")
            
            # Сохраняем timestamp последнего уведомления
            self.last_notification_timestamp = timestamp
            
            # Удаляем файл уведомления (чтобы не отправлять повторно)
            try:
                NOTIFICATION_FILE.unlink()
            except Exception as e:
                logger.warning(f"Не удалось удалить файл уведомления: {e}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON уведомления: {e}")
        except Exception as e:
            logger.error(f"Ошибка при проверке уведомлений: {e}")
    
    async def check_and_send_loop(self):
        """Основной цикл проверки уведомлений"""
        import asyncio
        logger.info("Запуск цикла проверки уведомлений...")
        
        while True:
            try:
                await self.check_notifications_simple()
                await asyncio.sleep(2)  # Проверяем каждые 2 секунды
            except Exception as e:
                logger.error(f"Ошибка в цикле проверки: {e}")
                await asyncio.sleep(5)
    
    async def check_notifications_simple(self):
        """Упрощённая проверка уведомлений без context"""
        import asyncio
        
        try:
            # Проверяем наличие файла с уведомлениями
            if not NOTIFICATION_FILE.exists():
                return
            
            # Читаем уведомление
            with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            timestamp = notification.get('timestamp')
            message = notification.get('message')
            
            # Проверяем, не отправляли ли мы уже это уведомление
            if timestamp == self.last_notification_timestamp:
                return
            
            # Отправляем уведомление всем подписчикам
            subscribers = self.db.get_all_subscribers()
            
            if not subscribers:
                logger.warning("Нет подписчиков для отправки уведомления")
                return
            
            sent_count = 0
            for chat_id in subscribers:
                try:
                    await self.app.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=None
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
            
            logger.info(f"Уведомление отправлено {sent_count} подписчикам")
            
            # Сохраняем timestamp последнего уведомления
            self.last_notification_timestamp = timestamp
            
            # Удаляем файл уведомления
            try:
                NOTIFICATION_FILE.unlink()
            except Exception as e:
                logger.warning(f"Не удалось удалить файл уведомления: {e}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON уведомления: {e}")
        except Exception as e:
            logger.error(f"Ошибка при проверке уведомлений: {e}")
    
    def run(self):
        """Запуск бота"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК TELEGRAM БОТА")
        logger.info("=" * 60)
        
        # Запускаем бота с кастомным циклом
        import asyncio
        
        async def main_loop():
            """Главный async цикл"""
            # Инициализируем бота
            await self.app.initialize()
            await self.app.start()
            
            logger.info("Бот запущен. Начинаем polling...")
            
            # Запускаем updater в фоне
            await self.app.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            logger.info("Polling запущен. Запускаем проверку уведомлений...")
            
            # Запускаем проверку уведомлений
            await self.check_and_send_loop()
        
        try:
            asyncio.run(main_loop())
        except KeyboardInterrupt:
            logger.info("Остановка бота...")
        except Exception as e:
            logger.exception(f"Ошибка в главном цикле: {e}")


def main():
    """Точка входа"""
    try:
        # Проверка токена
        if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            logger.error("TELEGRAM_BOT_TOKEN не установлен!")
            logger.error("Укажите токен в файле .env")
            sys.exit(1)
        
        # Создаём необходимые директории
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        NOTIFICATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Импортируем database только здесь, чтобы избежать циклических импортов
        sys.path.insert(0, '/app')
        
        # Запускаем бота
        bot = KadrBot(BOT_TOKEN)
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Критическая ошибка в боте: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

