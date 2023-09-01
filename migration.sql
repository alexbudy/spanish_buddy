PRAGMA foreign_keys=ON; -- does not persist, must be enabled on each connection

CREATE TABLE IF NOT EXISTS nouns (
  id INTEGER PRIMARY KEY,
  spanish TEXT NOT NULL,
  english TEXT NOT NULL,
  gender TEXT,
  UNIQUE(english)
);

CREATE TABLE IF NOT EXISTS profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP DEFAULT NULL,
  UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS rankings (
  profile_id INTEGER NOT NULL,
  noun_id INTEGER NOT NULL,
  en_to_es REAL NOT NULL DEFAULT 0,
  es_to_en REAL NOT NULL DEFAULT 0,
  FOREIGN KEY(profile_id) REFERENCES profiles(id),
  FOREIGN KEY(noun_id) REFERENCES nouns(id),
  UNIQUE(profile_id, noun_id)
);
