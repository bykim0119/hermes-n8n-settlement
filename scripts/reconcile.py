"""거래처별 주문수량 합 vs 정산수량을 대조해 불일치 건만 반환한다."""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "settlement.db"


def reconcile(db_path=DB):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        '''
        SELECT o."거래처" AS partner,
               SUM(o."주문수량") AS order_sum,
               s."정산수량"    AS settled
        FROM orders o
        JOIN settlement s ON o."거래처" = s."거래처"
        GROUP BY o."거래처"
        '''
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        diff = r["settled"] - r["order_sum"]
        if diff != 0:
            out.append({
                "partner": r["partner"],
                "order_sum": r["order_sum"],
                "settled": r["settled"],
                "diff": diff,
            })
    return out


def main():
    print(json.dumps(reconcile(), ensure_ascii=False))


if __name__ == "__main__":
    main()
