"""전체 파이프라인: 대조 → 조사 → 리포트(파일+디스코드).

`run_pipeline()`은 CLI(run_all.py)와 HTTP 서비스(serve.py /run)가 공유한다.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import investigate
import load_to_sqlite
import reconcile
import report

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"


def run_pipeline(post=True):
    """대조→조사→리포트 저장→(선택)디스코드 게시. 결과 dict를 반환한다.

    반환: {"results","summary","report_path","posted"}
    """
    load_to_sqlite.main()
    mismatches = reconcile.reconcile()
    results = [investigate.investigate(m["partner"], m["diff"]) for m in mismatches]

    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"settlement_{datetime.now():%Y%m%d_%H%M}.md"
    report.write_report(results, out)
    summary = report.summary_line(results)

    posted = False
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if post and webhook:
        content = summary + "\n\n" + report.render_markdown(results)
        try:
            report.post_discord(webhook, content[:1900])
            posted = True
        except Exception as e:  # 게시 실패해도 파일은 남음
            print(f"디스코드 게시 실패(무시): {e}", file=sys.stderr)

    return {
        "results": results,
        "summary": summary,
        "report_path": str(out),
        "posted": posted,
    }


def main():
    r = run_pipeline()
    print(f"리포트 저장: {r['report_path']}")
    print(r["summary"])
    if r["posted"]:
        print("디스코드 게시 완료")
    print(json.dumps(r["results"], ensure_ascii=False))


if __name__ == "__main__":
    main()
