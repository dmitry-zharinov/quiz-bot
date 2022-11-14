
import logging
import os

from dotenv import load_dotenv
from telegram import ForceReply, ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! Я бот для викторин!',
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu()
    )


def get_main_menu():
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт'],
    ]
    return ReplyKeyboardMarkup(custom_keyboard)


def main():
    load_dotenv()
    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    updater = Updater(tg_bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
