"""
Glowise 3.0
SQLite Database
"""

import sqlite3
import json

DATABASE_NAME = "glowise.db"


def connect():

    return sqlite3.connect(DATABASE_NAME)


def initialize_database():

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS analysis(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        image_path TEXT,

        skin_score INTEGER,

        skin_type TEXT,

        concerns TEXT,

        products TEXT,

        remedies TEXT,

        weather TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()

    conn.close()


def save_analysis(

    image_path,

    skin_score,

    skin_type,

    concerns,

    products,

    remedies,

    weather

):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO analysis(

        image_path,

        skin_score,

        skin_type,

        concerns,

        products,

        remedies,

        weather

    )

    VALUES(?,?,?,?,?,?,?)

    """,

    (

        image_path,

        skin_score,

        skin_type,

        json.dumps(concerns),

        json.dumps(products),

        json.dumps(remedies),

        json.dumps(weather)

    )

    )

    conn.commit()

    conn.close()


def get_history():

    conn = connect()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM analysis

    ORDER BY created_at DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return [

        dict(row)

        for row in rows

    ]


def get_latest():

    conn = connect()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM analysis

    ORDER BY created_at DESC

    LIMIT 1

    """)

    row = cursor.fetchone()

    conn.close()

    if row:

        return dict(row)

    return None


def delete_analysis(id):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM analysis WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()


if __name__ == "__main__":

    initialize_database()

    print("Database Ready")