import inquirer


def main():
    print(
        "Welcome to Spanish Buddy, where you can practice your spanish to english word translations!"
    )
    print("First, please choose or create a profile!")

    questions = [
        inquirer.List(
            "option",
            message="Select a profile (or exit)",
            choices=["NEW PROFILE 1", "NEW PROFILE 2", "NEW PROFILE 3", "Exit :("],
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
