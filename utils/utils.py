from dataclasses import dataclass
import sqlite3
from typing import List, Optional

db_path: str = "my_db.db"


@dataclass
class Word:
    """Word dataclass for a given profile id"""

    id: int
    profile_id: int
    spanish: str
    english: str
    gender: str
    es_to_en: float
    en_to_es: float


def init_profile(profile_name: str):
    conn = sqlite3.connect(db_path)

    cur = conn.cursor()
    cur.execute("INSERT INTO profiles (name) VALUES (:profile_name);", (profile_name,))

    profile_id: int = int(cur.lastrowid)

    cur.execute("SELECT id FROM nouns;")
    noun_ids = cur.fetchall()

    for noun_id in noun_ids:
        cur.execute(
            "INSERT INTO rankings (profile_id, noun_id) VALUES (:profile_id, :noun_id);",
            (
                profile_id,
                noun_id[0],
            ),
        )

    conn.commit()


def get_profiles() -> List[str]:
    conn = sqlite3.connect(db_path)

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM profiles WHERE deleted_at IS NULL ORDER BY created_at ASC LIMIT 3"
    )
    rows = cur.fetchall()

    return [row[1] for row in rows]


def get_words_for_profile(
    profile: str,
    num_words: int = 10,
    exclude_word_id: Optional[int] = None,
    locale: str = "es_to_en",
) -> List[Word]:
    """For a given `profile` -
    Return the `num_words` least known words in the given locale, excluding `exclude_word_id` id
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    qry: str = f"""SELECT n.id, r.profile_id, n.spanish, n.english, n.gender,
                          r.es_to_en, r.en_to_es
    FROM nouns n 
    INNER JOIN rankings r ON n.id = r.noun_id
    INNER JOIN profiles p on p.id = r.profile_id
    WHERE p.name = '{profile}' """

    if exclude_word_id:
        qry += f" AND n.id != {exclude_word_id} "

    qry += f" ORDER BY {locale} ASC LIMIT {num_words};"

    cur.execute(qry)
    rows = cur.fetchall()

    return [Word(*row) for row in rows]
