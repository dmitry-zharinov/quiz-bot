
import logging
import os
import random

import redis
from dotenv import load_dotenv
from telegram import (ForceReply, ParseMode, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from main import parse_quiz_from_file

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

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

    num, quiz_item = random.choice(list(quiz.items()))
    update.message.reply_text(quiz_item["question"])

    logger.info("Question to %s: %s", update.message.from_user.first_name, quiz_item["question"])
    logger.info("Answer: %s", quiz_item["answer"])
    #logger.info("Comment: %s", quiz_item["comment"])

    context.user_data["correct_answer"] = quiz_item["answer"]
    #context.user_data["comment"] = quiz_item["comment"]

    # записать вопрос в БД
    db.set(update.effective_user.id, quiz_item["question"])

    return QUIZ


def handle_solution_attempt(update, context):
    user_answer = update.message.text
    correct_answer = context.user_data["correct_answer"]
    #comment = context.user_data["comment"]

    reply = 'Неправильно… Попробуешь ещё раз?'
    if user_answer.lower() in correct_answer.lower():
        reply = f"Правильно! Для следующего вопроса нажми «Новый вопрос»"
        del context.user_data["correct_answer"]
        #del context.user_data["comment"]
    update.message.reply_text(reply,reply_markup=reply_markup)
    return QUIZ


def give_up(update, context):
    correct_answer = context.user_data["correct_answer"]
    if correct_answer:
        reply = (
            f"Правильный ответ: {correct_answer}\n"
            'Для продолжения нажмите кнопку "Новый вопрос"'
        )
        del context.user_data["correct_answer"]
    update.message.reply_text(reply,reply_markup=reply_markup)
    return QUIZ


def stats(update, context):
    update.message.reply_text('Статистика.')
    return QUIZ


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('До свидания! Пишите ещё, когда захотите.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
        
    updater = Updater(os.environ["TG_BOT_TOKEN"])

    db = redis.Redis(host=os.environ["REDIS_URL"],
                     port=os.environ["REDIS_PORT"],
                     password=os.environ["REDIS_PASSWORD"],)
    quiz = parse_quiz_from_file('quiz-questions/120br.txt')

    dispatcher = updater.dispatcher

    dispatcher.bot_data["db"] = db
    dispatcher.bot_data["quiz"] = quiz
    logger.info("test.")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ: [
                MessageHandler(
                    Filters.regex("Новый вопрос"), handle_new_question_request
                ),
                MessageHandler(Filters.regex("Мой счет"), stats),
                MessageHandler(Filters.regex("Сдаться"), give_up),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
