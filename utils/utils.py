from dataclasses import dataclass, field
import sqlite3
from typing import List, Optional

db_path: str = "my_db.db"


@dataclass
class Word:
    id: int
    spanish: str
    english: str
    gender: str
    spanish_with_article: str = field(init=False)

    def __post_init__(self):
        self.spanish_with_article = (
            {"m": "el", "f": "la"}[self.gender] + " " + self.spanish
        )


@dataclass
class Ranking:
    profile_id: int
    noun_id: int
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


def get_all_words(lang: str) -> List[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    qry: str = f"""SELECT n.id, n.spanish, n.english, n.gender FROM nouns n;"""
    cur.execute(qry)

    rows = cur.fetchall()
    words: List[str] = []
    for row in rows:
        word: Word = Word(*row)
        if lang == "en":
            words.append(word.english)
        else:
            words.append(word.spanish_with_article)

    return words


def update_ranking_for_word(word_id: int, locale: str, profile: str, got_correct: bool):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT id FROM profiles WHERE name = :profile", (profile,))
    p_id: int = cur.fetchone()[0]

    ranking_adjustment: float = [-0.5, 0.5][got_correct]
    qry: str = f"""UPDATE rankings SET {locale} = {locale} + ? WHERE profile_id=? AND noun_id = ?"""

    cur.execute(qry, (ranking_adjustment, p_id, word_id))
    conn.commit()
    conn.close()


def get_words_for_question(
    profile: str,
    num_words: int = 10,
    exclude_word_ids: List[int] = [],
    locale: str = "es_to_en",
) -> List[Word]:
    """For a given `profile` -
    Return the `num_words` least known words in the given locale, excluding `exclude_word_id` id
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    qry: str = f"""SELECT n.id, n.spanish, n.english, n.gender, r.profile_id, n.id,
                          r.es_to_en, r.en_to_es
    FROM nouns n 
    INNER JOIN rankings r ON n.id = r.noun_id
    INNER JOIN profiles p on p.id = r.profile_id
    WHERE p.name = '{profile}' """

    if exclude_word_ids:
        excluded_ids_str: str = ",".join(map(str, exclude_word_ids))
        qry += f" AND n.id NOT IN ({excluded_ids_str}) "

    qry += f" ORDER BY {locale} ASC, RANDOM() LIMIT {num_words};"

    cur.execute(qry)
    rows = cur.fetchall()

    return [Word(*row[:4]) for row in rows]
