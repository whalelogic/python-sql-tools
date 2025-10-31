# 🐬 MySQL to SQLite Converter 🐿️

A Python command-line tool that converts a MySQL `.sql` dump file into a working SQLite `.db` database file.  
Perfect for quickly migrating small databases or prototyping with SQLite.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Supported-MySQL%20%26%20MariaDB-yellow?logo=mysql">
  <img src="https://img.shields.io/badge/Output-SQLite%20DB-green?logo=sqlite">
</p>

---

## ✨ Features

- 🧹 **Cleans up MySQL-specific SQL** (types, keys, comments, `AUTO_INCREMENT`, `COLLATE`, etc)
- 🔄 **Converts INSERTs and schema** to valid SQLite syntax
- 🛑 **Skips MySQL session/control statements** (`SET`, `LOCK`, `DELIMITER`, `START TRANSACTION`, etc)
- 🐞 **Handles string escaping** and multi-line statements
- 💨 **Lightweight**: no dependencies beyond Python stdlib and [sqlparse](https://github.com/andialbrecht/sqlparse)

---

## 🚀 Usage

```sh
python mysql_to_sqlite.py input.sql output.sqlite
```

- **input.sql**: Your MySQL dump file (schema + data)
- **output.sqlite**: The SQLite database file to create

---

## 🏗️ Example

```sh
python mysql_to_sqlite.py ~/db/posts-ready.sql ~/db/posts-sqlite.db
```

---

## ⚙️ Requirements

- Python 3.7+
- [sqlparse](https://pypi.org/project/sqlparse/)  
  Install with:  
  ```sh
  pip install sqlparse
  OR
  pip install requirements.txt
  ```

---

## 📝 Notes

- Designed for simple MySQL/MariaDB dumps (schema + data).  
- For advanced MySQL features (stored procedures, triggers, etc), manual editing may be required.
- Not intended for production migrations—test your converted DB!

---

## 🐛 Troubleshooting

- If you see `near ...: syntax error`, check the output SQL for unhandled MySQL constructs.
- If you find a bug, open an issue or PR!

---

## 📦 License

MIT License

---

## 🙏 Credits

- Inspired by the many community migration scripts.
- Icons: [Twemoji](https://twemoji.twitter.com/), [Simple Icons](https://simpleicons.org/).

