import sqlite3
import pandas as pd

DB_PATH = "ravelry.db"

# connect to db
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# create tables on startup
def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patterns (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                slug        TEXT UNIQUE NOT NULL,
                scraped_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS projects (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id      INTEGER NOT NULL REFERENCES patterns(id),
                username        TEXT,
                yarn_name       TEXT,
                yarn_colorway   TEXT,
                project_notes   TEXT DEFAULT '',
                status          TEXT,
                date            TEXT,
                url             TEXT,
                sentiment       TEXT
            );
        """)
        
# save scraped projects for a pattern to the database
# if pattern exists, replaces existing projects for that pattern if already present
def save_dataframe(df, pattern_slug):

    with get_connection() as conn:
        # insert pattern if it doesn't exist
        conn.execute("""
            INSERT OR IGNORE INTO patterns (slug) VALUES (?)
        """, (pattern_slug,))

        # get pattern id
        pattern_id = conn.execute("""
            SELECT id FROM patterns WHERE slug = ?
        """, (pattern_slug,)).fetchone()[0]

        # replace existing projects for this pattern
        conn.execute("DELETE FROM projects WHERE pattern_id = ?", (pattern_id,))

        # insert new rows
        rows = df.copy()
        rows["pattern_id"] = pattern_id
        rows["sentiment"] = None
        rows.to_sql("projects", conn, if_exists="append", index=False)

# save predictions
def save_predictions(predictions_df, pattern_slug):
    with get_connection() as conn:
        pattern_id = conn.execute("""
            SELECT id FROM patterns WHERE slug = ?
        """, (pattern_slug,)).fetchone()

        if not pattern_id:
            raise ValueError(f"Pattern '{pattern_slug}' not found in database.")

        pattern_id = pattern_id[0]

        for _, row in predictions_df.iterrows():
            conn.execute("""
                UPDATE projects SET sentiment = ?
                WHERE pattern_id = ? AND username = ?
            """, (row["prediction"], pattern_id, row["username"]))


# load all projects for a pattern from the database.
def load_dataframe(pattern_slug):
    with get_connection() as conn:
        df = pd.read_sql("""
            SELECT pr.*
            FROM projects pr
            JOIN patterns p ON p.id = pr.pattern_id
            WHERE p.slug = ?
        """, conn, params=(pattern_slug,))

    if "project_notes" in df.columns:
        df["project_notes"] = df["project_notes"].fillna("")

    return df

# return all patterns stored in the database.
def load_all_patterns():
    with get_connection() as conn:
        return pd.read_sql("SELECT * FROM patterns", conn)

"""
# ARCHIVED, NOT USING EXCEL ANYMORE, WILL USE SQLITE DB
def save_dataframe(df, output_path):
    output_file = Path(output_path)
    df.to_excel(output_file, index=False)
    return output_file

def load_dataframe(input_path):
    input_file = Path(input_path)
    if not input_file.is_file():
        raise FileNotFoundError(f"Excel file not found: {input_file}")

    df = pd.read_excel(input_file)
    if "project_notes" in df.columns:
        df["project_notes"] = df["project_notes"].fillna("")
    return df
"""