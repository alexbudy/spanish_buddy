import random
from typing import List
import inquirer
import sqlite3

from utils.utils import (
    get_all_words,
    get_profiles,
    get_words_for_question,
    init_profile,
    Word,
)

database_path = "my_db.db"
EMPTY_PROFILE = "--NEW_PROFILE--"


def create_new_profile(cur, existing_profiles):
    existing_profiles_lowered = [e_p.lower() for e_p in existing_profiles]
    answer = inquirer.prompt(
        [
            inquirer.Text(
                "profile", message="What would you like to call this profile?"
            ),
        ]
    )
    new_profile: str = answer["profile"].strip()
    while (
        not new_profile
        or new_profile.lower() in existing_profiles_lowered
        or not new_profile.isalnum()
    ):
        if not new_profile:
            prompt = "Please enter a non-empty profile"
        elif new_profile.lower() in existing_profiles_lowered:
            prompt = f"Profile {new_profile} already exists, please enter a unique one"
        else:
            prompt = "Invalid profile name, please try again"
        answer = inquirer.prompt(
            [
                inquirer.Text("profile", message=prompt),
            ]
        )
        new_profile: str = answer["profile"].strip()

    print(f"Creating profile {new_profile}")
    init_profile(new_profile)


def training_loop(locale: str, profile: str):
    total_questions: int = 20
    num_correct: int = 0
    shown_words: List[int] = []
    all_words: List[str] = get_all_words(locale[:2])

    for i in range(1, total_questions + 1):
        words: List[Word] = get_words_for_question(profile, locale=locale)
        target_word: Word = random.choice(words)
        if locale[:2] == "es":
            target_word_str: str = target_word.english
            correct_translation: str = (
                {"m": "el", "f": "la"}[target_word.gender] + " " + target_word.spanish
            )
        else:
            target_word_str: str = target_word.spanish
            correct_translation: str = target_word.english

        answers: List[str] = random.sample(all_words, 5)
        if correct_translation in answers:
            answers.remove(correct_translation)

        answer_set: List[str] = answers[:4] + [correct_translation]
        random.shuffle(answer_set)

        locale_question = [
            inquirer.List(
                "selected_answer",
                message=f'{i}/{total_questions+1} Please select the translation for "{target_word_str}"',
                choices=answer_set,
            ),
        ]

        answer = inquirer.prompt(locale_question)
        selected_ans: str = answer["selected_answer"]
        print(f"Selected {selected_ans}")
        if selected_ans == correct_translation:
            print("Correct!")
        else:
            print("Wrong!")


def training_type_selection(profile: str):
    print("Please select training locale")
    locale_question = [
        inquirer.List(
            "locale",
            message="Select a training direction",
            choices=[
                "1. Provide spanish words, select english words",
                "2. Provide english words, select spanish words",
            ],
        ),
    ]

    answer = inquirer.prompt(locale_question)
    selected_option = answer["locale"]

    if selected_option.startswith("1."):
        locale: str = "es_to_en"
    else:
        locale: str = "en_to_es"

    training_loop(locale, profile)


def main():
    print(
        "Welcome to Spanish Buddy, where you can practice your spanish to english word translations!"
    )
    print("First, please choose or create a profile!")

    conn = sqlite3.connect(database_path)
    cur = conn.cursor()

    existing_profiles: List[str] = get_profiles()

    questions = [
        inquirer.List(
            "option",
            message="Select a profile (or exit)",
            choices=existing_profiles
            + [EMPTY_PROFILE for _ in range(3 - len(existing_profiles))]
            + ["Exit :("],
        ),
    ]

    answers = inquirer.prompt(questions)

    selected_option = answers["option"]
    if selected_option.startswith("Exit"):
        print("Exiting the program, thanks for training!")
    elif EMPTY_PROFILE in selected_option:
        print("Empty profile selected... Creating new profile!")
        create_new_profile(cur, existing_profiles)
        conn.commit()
    else:
        print(f"Selected {selected_option}, loading profile data!")
        training_type_selection(selected_option)


if __name__ == "__main__":
    main()
