"""주문상세·정산마감 CSV를 SQLite(settlement.db)로 적재한다."""
import csv
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DB = DATA / "settlement.db"

INT_COLS = {
    "상품순번", "상품수량", "덤상품수량", "매출액", "초기자재수량",
    "주문수량", "취소수량", "반품수량", "정산수량",
}


def load_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def create_table(cur, name, rows):
    cols = list(rows[0].keys())
    defs = ", ".join(
        (f'"{c}" INTEGER' if c in INT_COLS else f'"{c}" TEXT') for c in cols
    )
    cur.execute(f"DROP TABLE IF EXISTS {name}")
    cur.execute(f"CREATE TABLE {name} ({defs})")
    collist = ", ".join(f'"{c}"' for c in cols)
    placeholders = ", ".join("?" for _ in cols)
    for r in rows:
        vals = []
        for c in cols:
            v = r[c]
            if c in INT_COLS and v not in ("", None):
                vals.append(int(v))
            else:
                vals.append(v)
        cur.execute(f"INSERT INTO {name} ({collist}) VALUES ({placeholders})", vals)


def main():
    orders = load_csv(DATA / "주문상세.csv")
    settle = load_csv(DATA / "정산마감.csv")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    create_table(cur, "orders", orders)
    create_table(cur, "settlement", settle)
    conn.commit()
    conn.close()
    print(f"loaded orders={len(orders)} settlement={len(settle)} -> {DB}")


if __name__ == "__main__":
    main()
