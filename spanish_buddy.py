from typing import List
import inquirer
import sqlite3

database_path = "my_db.db"


def get_profiles() -> List[str]:
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM profiles WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 3"
    )
    rows = cur.fetchall()

    return [row[1] for row in rows]


def main():
    print(
        "Welcome to Spanish Buddy, where you can practice your spanish to english word translations!"
    )
    print("First, please choose or create a profile!")

    profiles = get_profiles()
    while len(profiles) < 3:
        profiles.append("--EMPTY_PROFILE--")

    questions = [
        inquirer.List(
            "option",
            message="Select a profile (or exit)",
            choices=profiles + ["Exit :("],
        ),
    ]

    answers = inquirer.prompt(questions)

    selected_option = answers["option"]
    if selected_option.startswith("Exit"):
        print("Exiting the program.")
    else:
        print(f"You selected: {selected_option}")


if __name__ == "__main__":
    main()
