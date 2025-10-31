import re
import sys
import sqlite3
import sqlparse
from pathlib import Path

def mysql_to_sqlite(mysql_sql: str) -> str:
    output = []
    for stmt in sqlparse.split(mysql_sql):
        stmt = stmt.strip()
        if not stmt:
            continue

        # Skip MySQL-specific statements entirely
        skip_prefixes = [
            "LOCK TABLES", "UNLOCK TABLES", "DELIMITER", "SET ", "/*!",
            "USE ", "DROP DATABASE", "CREATE DATABASE",
            "START TRANSACTION", "BEGIN", "COMMIT", "ROLLBACK"
            ]
        if any(stmt.upper().startswith(prefix) for prefix in skip_prefixes):
            continue

        # Remove backticks
        stmt = stmt.replace('`', '')

        # Remove table options and COLLATE after closing parens
        stmt = re.sub(r'\)\s*(ENGINE|AUTO_INCREMENT|DEFAULT CHARSET|CHARACTER SET|COLLATE)[^;]*;', ')', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'COLLATE\s*=?\s*\w+(_\w+)?', '', stmt, flags=re.IGNORECASE)

        # Remove comments
        stmt = re.sub(r'COMMENT\s+\'[^\']*\'', '', stmt, flags=re.IGNORECASE)

        # Remove "ON UPDATE ..." clauses
        stmt = re.sub(r'ON UPDATE\s+current_timestamp\s*\(?\)?', '', stmt, flags=re.IGNORECASE)

        # Replace AUTO_INCREMENT primary key
        stmt = re.sub(
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:int|integer)\s*\(\d+\)\s+NOT\s+NULL\s+AUTO_INCREMENT',
            r'\1 INTEGER PRIMARY KEY AUTOINCREMENT',
            stmt,
            flags=re.IGNORECASE
        )
        stmt = re.sub(r'\bAUTO_INCREMENT\b', '', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r',\s*PRIMARY KEY\s*\([^)]+\)', '', stmt, flags=re.IGNORECASE)

        # Replace types
        stmt = re.sub(r'\bint\s*\(\s*\d+\s*\)', 'INTEGER', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\bvarchar\s*\(\s*\d+\s*\)', 'TEXT', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\blongtext\b', 'TEXT', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\btext\b', 'TEXT', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\bdatetime\b', 'TEXT', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\btinyint\s*\(\s*1\s*\)', 'BOOLEAN', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\btinyint\s*\(\s*\d+\s*\)', 'INTEGER', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\bUNSIGNED\b', '', stmt, flags=re.IGNORECASE)

        # Replace ENUM/SET with TEXT
        stmt = re.sub(r'\bENUM\s*\(.*?\)', 'TEXT', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r'\bSET\s*\(.*?\)', 'TEXT', stmt, flags=re.IGNORECASE)

        # Handle UNIQUE KEY and KEY
        stmt = re.sub(r'UNIQUE\s+KEY\s+\w+\s*\(([^)]+)\)', r'UNIQUE(\1)', stmt, flags=re.IGNORECASE)
        stmt = re.sub(r',?\s*KEY\s+\w+\s*\([^)]+\)', '', stmt, flags=re.IGNORECASE)

        # Remove double commas and stray commas before )
        stmt = re.sub(r',\s*,', ',', stmt)
        stmt = re.sub(r',\s*\)', ')', stmt)

        # Fix current_timestamp()
        stmt = re.sub(r'current_timestamp\s*\(\)', 'current_timestamp', stmt, flags=re.IGNORECASE)

        # Clean whitespace
        stmt = re.sub(r'\s+', ' ', stmt).strip()
        stmt = fix_quotes(stmt)

        if stmt:
            output.append(stmt)

    return ';\n'.join(output) + ';' if output else ''


def format_sql_block(sql: str) -> str:
    return sqlparse.format(sql, reindent=True, keyword_case='upper')


def fix_quotes(s):
    # Only replace inside quoted strings
    # This simple version works for most cases:
    return re.sub(r"\\'", "''", s)


def convert_sql_file(mysql_dump_file: str, sqlite_output_file: str):
    mysql_sql = Path(mysql_dump_file).read_text(encoding='utf-8')
    sqlite_sql = mysql_to_sqlite(mysql_sql)
    conn = sqlite3.connect(sqlite_output_file)
    cursor = conn.cursor()
    try:
        statements = sqlparse.split(sqlite_sql)
        for statement in statements:
            s = statement.strip()
            if s:
                print("⚠️ Executing SQL:\n" + format_sql_block(s) + "\n")
                cursor.executescript(s + (';' if not s.endswith(';') else ''))
        conn.commit()
        print(f" Converted and saved to {sqlite_output_file}")
    except sqlite3.Error as e:
        print(f" SQLite error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python mysql_to_sqlite.py input.sql output.sqlite")
        sys.exit(1)
    mysql_dump = sys.argv[1]
    sqlite_file = sys.argv[2]
    convert_sql_file(mysql_dump, sqlite_file)
