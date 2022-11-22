from itertools import count
import os
from dotenv import load_dotenv


def parse_quiz_from_file(filepath):
    quiz = {}
    question = ''
    answer = ''
    comment = ''

    counter = count()
    number = next(counter)

    with open(filepath, "r", encoding="KOI8-R") as file:
        for text in file.read().split("\n\n"):
            if not text:
                continue
            header, body = text.split("\n", maxsplit=1)
            if header.lower().strip().startswith("вопрос"):
                question = " ".join(body.split())

            if header.lower().strip().startswith("ответ"):
                answer = " ".join(body.split())

            if header.lower().strip().startswith("комментарий"):
                comment = " ".join(body.split())

            if header.lower().strip().startswith("автор"):
                quiz[number] = {
                    "question": question,
                    "answer": answer,
                    "comment": comment,
                }

                number = next(counter)
                question = ''
                answer = ''
                comment = ''

    return quiz
