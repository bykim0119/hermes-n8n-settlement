import sqlite3
from pathlib import Path

import load_to_sqlite

DB = Path(__file__).resolve().parent.parent / "data" / "settlement.db"


def test_load_creates_tables_and_sums():
    load_to_sqlite.main()
    conn = sqlite3.connect(DB)
    # 행 수
    assert conn.execute("SELECT COUNT(*) FROM settlement").fetchone()[0] == 5
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] >= 15
    # 거래처A 주문수량 합 = 120 (정답지 기준)
    total = conn.execute(
        'SELECT SUM("주문수량") FROM orders WHERE "거래처" = ?', ("거래처A",)
    ).fetchone()[0]
    assert total == 120
    # 숫자 칸이 INTEGER로 적재되어 산술 비교가 됨
    assert conn.execute('SELECT SUM("정산수량") FROM settlement').fetchone()[0] == 110 + 92 + 54 + 45 + 30
    conn.close()
