"""조사 결과를 마크다운 리포트와 요약줄로 렌더링하고 파일로 저장한다."""
import json
import urllib.request
from datetime import datetime


def summary_line(results):
    ok = sum(1 for r in results if r["verdict"] == "정상")
    esc = sum(1 for r in results if r["verdict"] == "에스컬레이션")
    return f"정산 대사: {len(results)}건 중 정상 {ok}건, 확인 필요 {esc}건"


def render_markdown(results):
    ok = sum(1 for r in results if r["verdict"] == "정상")
    esc = sum(1 for r in results if r["verdict"] == "에스컬레이션")
    fail = sum(1 for r in results if r["verdict"] == "조사실패")
    lines = [
        f"# 정산 대사 리포트 ({datetime.now():%Y-%m-%d %H:%M})",
        "",
        f"- 검토 불일치: {len(results)}건",
        f"- 정상 자동해명: {ok}건",
        f"- 에스컬레이션: {esc}건",
    ]
    if fail:
        lines.append(f"- 조사 실패: {fail}건")
    lines += ["", "| 거래처 | 차이 | 판정 | 근거 |", "|---|---|---|---|"]
    for r in results:
        lines.append(f'| {r["partner"]} | {r["diff"]:+d} | {r["verdict"]} | {r["reason"]} |')
    return "\n".join(lines) + "\n"


def write_report(results, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_markdown(results))


def post_discord(webhook_url, content):
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data, headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=15)
