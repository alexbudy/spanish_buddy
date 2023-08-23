import sqlite3

db_path: str = "my_db.db"


def init_profile(profile_name: str):
    conn = sqlite3.connect(db_path)

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
