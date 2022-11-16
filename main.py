from random import randint
from itertools import count


def parse_quiz_from_file(filepath):
    quiz = {}
    question = ''
    answer = ''
    comment = ''

    counter = count()
    number = next(counter)

    with open(filepath, "r", encoding="KOI8-R") as file:    
        for text in file.read().split("\n\n"):
            print(text)
            if not text:
                continue
            header, body = text.split("\n", maxsplit=1)
            if header.lower().strip().startswith("вопрос"):
                question = " ".join(body.split())

            if header.lower().strip().startswith("ответ"):
                answer = " ".join(body.split())

            if header.lower().strip().startswith("комментарий"):
                comment = " ".join(body.split())

            if question and answer:
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


def main():
    quiz = parse_quiz_from_file('quiz-questions/120br.txt')
    for key, val in quiz.items():
        print(f'key: {key}')
        print(f'val: {val}')


if __name__ == "__main__":
    main()