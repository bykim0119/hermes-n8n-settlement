import json
from unittest import mock

import report

SAMPLE = [
    {"partner": "거래처A", "diff": -10, "verdict": "정상", "reason": "취소6+반품4"},
    {"partner": "거래처B", "diff": 12, "verdict": "정상", "reason": "덤 12"},
    {"partner": "거래처C", "diff": -6, "verdict": "에스컬레이션", "reason": "4개 불명"},
]


def test_summary_line_counts():
    assert report.summary_line(SAMPLE) == "정산 대사: 3건 중 정상 2건, 확인 필요 1건"


def test_render_markdown_has_all_partners_and_verdicts():
    md = report.render_markdown(SAMPLE)
    for p in ("거래처A", "거래처B", "거래처C"):
        assert p in md
    assert "에스컬레이션" in md
    assert "| 거래처 | 차이 | 판정 | 근거 |" in md


def test_post_discord_posts_json_content():
    with mock.patch("urllib.request.urlopen") as m:
        report.post_discord("https://discord.test/webhook", "요약 한 줄")
        assert m.called
        req = m.call_args[0][0]
        body = json.loads(req.data.decode())
        assert body["content"] == "요약 한 줄"
