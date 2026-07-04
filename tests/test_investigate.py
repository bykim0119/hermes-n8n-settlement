import investigate


def test_build_prompt_includes_partner_and_diff():
    p = investigate.build_prompt("거래처C", -6)
    assert "거래처C" in p
    assert "-6" in p
    assert "VERDICT:" in p and "REASON:" in p


def test_parse_verdict_normal():
    out = "조사 내용...\nVERDICT: 정상\nREASON: 취소6 반품4로 설명됨"
    r = investigate.parse_verdict(out)
    assert r == {"verdict": "정상", "reason": "취소6 반품4로 설명됨"}


def test_parse_verdict_escalation():
    out = "VERDICT: 에스컬레이션\nREASON: 4개 원인 불명"
    r = investigate.parse_verdict(out)
    assert r["verdict"] == "에스컬레이션"


def test_parse_verdict_malformed_returns_none():
    assert investigate.parse_verdict("판정 없음 그냥 텍스트") is None
