
import logging
import os
import random
import time
from parser import parse_quiz_from_file

import redis
from dotenv import load_dotenv
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from bot_logging import TelegramLogsHandler

logger = logging.getLogger('tg-bot')

QUIZ = 1

reply_keyboard = [
    ['Новый вопрос', 'Сдаться'],
    ['Мой счёт'],
]
reply_markup = ReplyKeyboardMarkup(reply_keyboard)


def start(update, context):
    logger.info("Start bot.")
    update.message.reply_text(
        text='Привет! Я бот для викторин!',
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    return QUIZ


def handle_new_question_request(update, context):
    db = context.bot_data["db"]
    quiz = context.bot_data["quiz"]

    _, quiz_item = random.choice(list(quiz.items()))
    update.message.reply_text(quiz_item["question"])

    context.user_data["correct_answer"] = quiz_item["answer"]
    context.user_data["comment"] = quiz_item["comment"]

    db.set(update.effective_user.id, quiz_item["question"])

    return QUIZ


def handle_answer(update, context):
    user_answer = update.message.text
    correct_answer = context.user_data["correct_answer"]
    comment = context.user_data["comment"]

    reply = 'Неправильно… Попробуешь ещё раз?'
    if user_answer.lower() in correct_answer.lower():

        reply = (
            f"Правильно!\n"
            f"{comment}\n"
            'Для следующего вопроса нажми «Новый вопрос»'
        )
        del context.user_data["correct_answer"]
        del context.user_data["comment"]

    update.message.reply_text(reply, reply_markup=reply_markup)
    return QUIZ


def give_up(update, context):
    correct_answer = context.user_data["correct_answer"]
    comment = context.user_data["comment"]
    if correct_answer:
        reply = (
            f"Правильный ответ: {correct_answer}\n"
            f"{comment}\n"
            'Для продолжения нажмите кнопку «Новый вопрос»'
        )
        del context.user_data["correct_answer"]
    update.message.reply_text(reply, reply_markup=reply_markup)
    return QUIZ


def user_score(update, context):
    update.message.reply_text('Статистика.')
    return QUIZ


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('До свидания! Пишите ещё, когда захотите.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    logger.warning('Update "%s" caused error"', update)


def run_bot(token, db, quiz):
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.bot_data["db"] = db
    dispatcher.bot_data["quiz"] = quiz

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ: [
                MessageHandler(
                    Filters.regex("Новый вопрос"),
                    handle_new_question_request
                ),
                MessageHandler(Filters.regex("Мой счет"),
                               user_score),
                MessageHandler(Filters.regex("Сдаться"),
                               give_up),
                MessageHandler(Filters.text,
                               handle_answer),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


def main():
    load_dotenv()

    token = os.environ["TG_BOT_TOKEN"]
    admin_user = os.environ["ADMIN_USER"]
    logging.basicConfig(level=logging.INFO)
    logger.addHandler(
        TelegramLogsHandler(token, admin_user)
    )

    db = redis.Redis(host=os.environ["REDIS_URL"],
                     port=os.environ["REDIS_PORT"],
                     password=os.environ["REDIS_PASSWORD"],)
    quiz = parse_quiz_from_file(os.environ["QUIZ_FILE"])

    run_bot(token, db, quiz)


if __name__ == '__main__':
    main()
