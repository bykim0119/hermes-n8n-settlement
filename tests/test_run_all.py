from unittest import mock

import run_all


def test_run_pipeline_writes_report_and_returns_summary(tmp_path, monkeypatch):
    # 실제 hermes 호출을 대체: 불일치 건마다 '정상' 판정 반환
    def fake_investigate(partner, diff, timeout=180):
        return {"partner": partner, "diff": diff, "verdict": "정상", "reason": "테스트"}

    monkeypatch.setattr(run_all.investigate, "investigate", fake_investigate)
    monkeypatch.setattr(run_all, "REPORTS", tmp_path)
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)

    r = run_all.run_pipeline()

    assert r["posted"] is False  # 웹훅 없으면 게시 안 함
    assert "정산 대사:" in r["summary"]
    assert len(r["results"]) == 3  # 정답지 불일치 3건
    report_file = tmp_path / r["report_path"].split("/")[-1]
    assert report_file.exists()
    assert "거래처C" in report_file.read_text(encoding="utf-8")


def test_run_pipeline_posts_when_webhook_set(tmp_path, monkeypatch):
    def fake_investigate(partner, diff, timeout=180):
        return {"partner": partner, "diff": diff, "verdict": "정상", "reason": "t"}

    monkeypatch.setattr(run_all.investigate, "investigate", fake_investigate)
    monkeypatch.setattr(run_all, "REPORTS", tmp_path)
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.test/webhook")

    with mock.patch("report.post_discord") as m:
        r = run_all.run_pipeline()
        assert m.called
        assert r["posted"] is True
