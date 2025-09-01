import argparse
import sqlite3
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/books.db")
    ap.add_argument("--table", default="books")
    ap.add_argument("--limit", type=int, default=20, help="Quantidade de registros a manter")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB não encontrado: {db_path}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # recria a tabela apenas com N registros
    cur.executescript(f"""
    DROP TABLE IF EXISTS __tmp_books__;
    CREATE TABLE __tmp_books__ AS
      SELECT * FROM {args.table} ORDER BY id LIMIT {args.limit};
    DROP TABLE {args.table};
    ALTER TABLE __tmp_books__ RENAME TO {args.table};
    """)

    con.commit()
    total = cur.execute(f"SELECT COUNT(*) FROM {args.table}").fetchone()[0]
    con.close()

    print(f"Reset concluído: {total} registros mantidos em {db_path}")

if __name__ == "__main__":
    main()