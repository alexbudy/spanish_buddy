from typing import List
import inquirer
import sqlite3

from utils.utils import get_profiles, get_words_for_profile, init_profile, Word

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


def training_type_selection(profile: str):
    words: List[Words] = get_words_for_profile(profile)


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
