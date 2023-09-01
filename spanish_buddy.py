import random
from typing import List
import inquirer
from inquirer import errors
import sqlite3

from utils.utils import (
    get_all_words,
    get_profiles,
    get_words_for_question,
    init_profile,
    Word,
    update_ranking_for_word,
)

database_path = "my_db.db"
EMPTY_PROFILE = "--NEW_PROFILE--"


def create_new_profile(cur, existing_profiles) -> str:
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

    return new_profile


def validate_num_questions(_, num_q):
    try:
        num_q = int(num_q)
        if num_q <= 0:
            raise errors.ValidationError(
                "", reason="Number of questions cannot be negative or 0."
            )
        if num_q > 20:
            raise errors.ValidationError(
                "",
                reason="Let's just stick a reasonable number of questions for now (<= 20)",
            )
    except ValueError:
        raise errors.ValidationError("", reason="Please enter a valid integer")

    return True


def validate_num_options(_, num_o):
    try:
        num_o = int(num_o)
        if num_o < 2:
            raise errors.ValidationError("", reason="Number of options must be >= 2.")
        if num_o > 6:
            raise errors.ValidationError(
                "",
                reason="Number of options cannot exceed 6.",
            )
    except ValueError:
        raise errors.ValidationError("", reason="Please enter a valid integer")

    return True


def training_loop(locale: str, profile: str):
    answers = inquirer.prompt(
        [
            inquirer.Text(
                "num_questions",
                message="How many questions would you like to solve? (1-20)",
                validate=validate_num_questions,
                default=10,
            )
        ]
    )

    total_questions: int = int(answers["num_questions"])

    answers = inquirer.prompt(
        [
            inquirer.Text(
                "num_options",
                message="How many options would you like to see per word? (2-6)",
                validate=validate_num_options,
                default=4,
            )
        ]
    )
    num_options: int = int(answers["num_options"])
    questions_correct: int = 0
    questioned_word_ids: List[int] = []
    incorrect_words: List[Word] = []
    all_words: List[str] = get_all_words(
        locale[-2:]
    )  # these are the words for the mult. choice answers

    for i in range(1, total_questions + 1):
        words: List[Word] = get_words_for_question(
            profile, locale=locale, exclude_word_ids=questioned_word_ids
        )
        target_word: Word = random.choice(words)
        if locale[:2] == "en":
            target_word_str: str = target_word.english
            correct_translation: str = target_word.spanish
        else:
            target_word_str: str = target_word.spanish
            correct_translation: str = target_word.english

        answers: List[str] = random.sample(all_words, num_options)
        if correct_translation in answers:
            answers.remove(correct_translation)

        answer_set: List[str] = answers[: num_options - 1] + [correct_translation]
        random.shuffle(answer_set)

        locale_question = [
            inquirer.List(
                "selected_answer",
                message=f'{i}/{total_questions} Please select the translation for "{target_word_str}"',
                choices=answer_set,
                carousel=True,
            ),
        ]

        answer = inquirer.prompt(locale_question)
        selected_ans: str = answer["selected_answer"]
        print(f"Selected {selected_ans}")
        if selected_ans == correct_translation:
            print("Correct! Adjusting ranking...")
            questions_correct += 1
        else:
            print("Wrong! Adjusting ranking...")
            incorrect_words.append(target_word)
        update_ranking_for_word(
            target_word.id,
            locale,
            profile,
            selected_ans == correct_translation,
            ranking_adjustment=0.15 * num_options,
        )

        questioned_word_ids.append(target_word.id)

    print(
        f"\nQuiz complete! You got {questions_correct}/{total_questions} = {round((questions_correct/total_questions) * 100)}% correct."
    )
    if questions_correct == total_questions:
        print("\nLooks like you know all the words given!")
    else:
        print("\nHere are the words you got wrong for review...")
        for word in incorrect_words:
            if locale[:2] == "en":
                print(f"    {word.english}: {word.spanish}\n")
            else:
                print(f"    {word.spanish}:{word.english}\n")

    print("\nStoring personal results\n")

    locale_question = [
        inquirer.List(
            "go_again",
            message=f"Would you like to go again?",
            choices=["Yes", "No"],
            carousel=True,
        ),
    ]
    answer = inquirer.prompt(locale_question)

    if answer["go_again"] == "Yes":
        training_loop(locale, profile)


def training_type_selection(profile: str):
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
            carousel=True,
        ),
    ]

    answers = inquirer.prompt(questions)

    selected_option = answers["option"]
    if selected_option.startswith("Exit"):
        print("Exiting the program, thanks for training!")
    elif EMPTY_PROFILE in selected_option:
        print("Empty profile selected... Creating new profile!")
        selected_option = create_new_profile(cur, existing_profiles)
    else:
        print(f"Selected {selected_option}, loading profile data!")

    training_type_selection(selected_option)


if __name__ == "__main__":
    main()
