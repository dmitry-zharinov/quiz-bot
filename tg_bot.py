
import logging
import os
import random

import redis
from dotenv import load_dotenv
from telegram import (ForceReply, ParseMode, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from main import parse_quiz_from_file

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


questions = parse_quiz_from_file('quiz-questions/120br.txt')

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


def clear(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                     text="Очищено!",
                     reply_markup=ReplyKeyboardRemove())


def ask_question(update: Update, context: CallbackContext):
    db = context.bot_data["db"]
    
    logger.info(update.effective_user)

    if update.message.text == 'Новый вопрос':
        question_num, question = random.choice(list(questions.items()))
        answer = questions[question_num]
        update.message.reply_text(question)
        
        # записать вопрос в БД
        db.set(update.effective_user.id, question)



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

    db = redis.Redis(host=os.environ["REDIS_URL"],
                     port=os.environ["REDIS_PORT"],
                     password=os.environ["REDIS_PASSWORD"],)

    dispatcher = updater.dispatcher

    dispatcher.bot_data["db"] = db
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("clear", clear))
    dispatcher.add_handler(MessageHandler(Filters.text, ask_question))
   # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
