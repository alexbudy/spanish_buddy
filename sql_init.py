import csv
from multiprocessing import connection
import sqlite3
import argparse
import os

migration_file_path = "migration.sql"


def initialize_db(database_path: str):
    conn = sqlite3.connect(database_path)

    cursor = conn.cursor()
    with open(migration_file_path) as f:
        script = f.read()
        cursor.executescript(script)
    conn.commit()

    load_nouns(cursor)
    conn.commit()


def load_nouns(cursor):
    with open("words/nouns.csv", "r", encoding="UTF-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            cursor.execute(
                "INSERT INTO nouns (spanish, english, gender) VALUES (:spanish, :english, :gender)",
                (row["spanish"], row["english"], row["gender"]),
            )


def init_profile(database_path: str, profile_name: str):
    conn = sqlite3.connect(database_path)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (name) VALUES (:profile_name);", (profile_name,)
    )

    profile_id: int = int(cursor.lastrowid)

    cursor.execute("SELECT id FROM nouns;")
    noun_ids = cursor.fetchall()

    for noun_id in noun_ids:
        cursor.execute(
            "INSERT INTO ranking (profile_id, noun_id) VALUES (:profile_id, :noun_id);",
            (
                profile_id,
                noun_id[0],
            ),
        )

    conn.commit()


if __name__ == "__main__":
    db_path = "my_db.db"

    parser = argparse.ArgumentParser()

    parser.add_argument("-ddb", "--drop-db", default=False, action="store_true")
    # add a default profile if dropping DB, TODO potentially add multiple options (profiles)
    parser.add_argument("-ap", "--add_profile", type=str, default=None)

    args = parser.parse_args()
    if args.drop_db:
        os.remove(db_path)

    initialize_db(db_path)

    if args.drop_db and args.add_profile:
        profile = args.add_profile
        init_profile(db_path, profile)
