import logging
import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from parser import parse_quiz_from_file
from bot_logging import TelegramLogsHandler


logger = logging.getLogger('vk-bot')

KEYBOARD = VkKeyboard()
KEYBOARD.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
KEYBOARD.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
KEYBOARD.add_line()
KEYBOARD.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)


def send_message(event, vk_api, message):
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=KEYBOARD.get_keyboard(),
    )


def start(event, vk_api):
    logger.info("Start bot.")
    send_message(event, vk_api, "Привет! Я бот для викторин!")


def ask_question(event, vk_api, db, quiz):
    _, quiz_item = random.choice(list(quiz.items()))
    correct_answer = quiz_item["answer"]
    question = quiz_item["question"]
    db.set(f"{event.user_id}_answer", correct_answer)
    db.set(f"{event.user_id}_comment", quiz_item["comment"])
    send_message(event, vk_api, question)


def check_answer(event, vk_api, db):
    message = 'Сначала надо задать вопрос. Нажмите кнопку "Новый вопрос"'

    user_answer = event.text
    correct_answer = db.get(f"{event.user_id}_answer")
    if correct_answer:
        correct_answer = correct_answer.decode()
        message = "Неправильно… Попробуешь ещё раз?"
        if user_answer.lower() in correct_answer.lower():
            comment = db.get(f"{event.user_id}_comment").decode()
            message = (
                f"Правильно!\n"
                f"{comment}\n"
                'Для следующего вопроса нажми «Новый вопрос»'
            )
            db.delete(f"{event.user_id}_answer")
            db.delete(f"{event.user_id}_comment")
    send_message(event, vk_api, message)


def give_up(event, vk_api, db):
    message = 'Сначала надо задать вопрос. Нажмите кнопку "Новый вопрос"'

    correct_answer = db.get(f"{event.user_id}_answer")
    if correct_answer:
        correct_answer = correct_answer.decode()
        comment = db.get(f"{event.user_id}_comment").decode()
        message = (
            f"Правильный ответ: {correct_answer}\n"
            f"{comment}\n"
            'Для продолжения нажмите кнопку «Новый вопрос»'
        )
        db.delete(f"{event.user_id}_answer")
        db.delete(f"{event.user_id}_comment")
    send_message(event, vk_api, message)


def show_user_score(event, vk_api, db):
    send_message(event, vk_api, "Статистика")


def run_bot(token):
    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() == "Старт":
                start(event, vk_api)
            elif event.text == "Новый вопрос":
                ask_question(event, vk_api, db, quiz)
            elif event.text == "Сдаться":
                give_up(event, vk_api, db)
            elif event.text == "Мой счет":
                show_user_score(event, vk_api, db)
            else:
                check_answer(event, vk_api, db)


if __name__ == "__main__":
    load_dotenv()
    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_admin_user = os.environ["ADMIN_USER"]
    logging.basicConfig(level=logging.INFO)
    logger.addHandler(
        TelegramLogsHandler(tg_bot_token, tg_admin_user)
    )

    db = redis.Redis(host=os.environ["REDIS_URL"],
                     port=os.environ["REDIS_PORT"],
                     password=os.environ["REDIS_PASSWORD"],)
    quiz = parse_quiz_from_file(os.environ["QUIZ_FILE"])

    vk_token = os.environ["VK_GROUP_TOKEN"]
    while True:
        try:
            run_bot(vk_token)
        except Exception as err:
            logger.exception(err)
            continue
