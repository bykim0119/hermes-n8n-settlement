import load_to_sqlite
import reconcile


def test_reconcile_flags_only_mismatches():
    load_to_sqlite.main()  # DB 준비
    result = reconcile.reconcile()
    by = {r["partner"]: r["diff"] for r in result}
    # 불일치 3건만, 정답지 부호(정산-주문합)
    assert by == {"거래처A": -10, "거래처B": 12, "거래처C": -6}
    # 오탐 0: D·E는 없음
    assert "거래처D" not in by and "거래처E" not in by
