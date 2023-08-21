from multiprocessing import connection
import sqlite3
import argparse
import os

migration_file_path = "migration.sql"

def initialize_db(database_path: str):
  conn = sqlite3.connect(database_path)
  conn.execute("PRAGMA foreign_keys = ON;")
  
  cursor = conn.cursor()
  with open(migration_file_path) as f:
    script = f.read()
    cursor.executescript(script)
  

if __name__ == "__main__":
  db_path = "my_db.db"
  
  parser = argparse.ArgumentParser()
  
  parser.add_argument("--drop-db", default=False, action='store_true')
  
  args = parser.parse_args()
  if args.drop_db:
    os.remove(db_path)
  
  initialize_db(db_path)