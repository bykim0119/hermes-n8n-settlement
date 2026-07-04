"""불일치 건을 hermes 에이전트에게 넘겨 원인을 조사·판정한다."""
import json
import os
import re
import subprocess
import sys

HERMES_BIN = os.environ.get(
    "HERMES_BIN", "/home/bykim0119/.venvs/hermes-agent/bin/hermes"
)

PROMPT_TEMPLATE = """당신은 정산 대사 조사원입니다. settlement_db 도구로 SQLite의 orders 테이블을 조회할 수 있습니다.
orders에는 거래처, 주문수량, 취소수량, 반품수량, 덤상품수량, 사은품여부, 상품명 등의 칸이 있습니다.

거래처 "{partner}"의 정산 대사에서 차이(정산수량 - 주문수량합)가 {diff}로 나왔습니다.
orders에서 이 거래처의 취소수량·반품수량·덤상품수량·사은품여부를 조회해 차이의 원인을 설명하세요.
차이가 취소·반품·덤·사은품으로 모두 설명되면 '정상', 설명되지 않는 수량이 남으면 '에스컬레이션'입니다.

반드시 마지막에 아래 두 줄을 정확히 이 형식으로 출력하세요:
VERDICT: 정상
REASON: <한 문장 근거>
(에스컬레이션이면 VERDICT: 에스컬레이션)"""


def build_prompt(partner, diff):
    return PROMPT_TEMPLATE.format(partner=partner, diff=diff)


def parse_verdict(output):
    v = re.search(r"^VERDICT:\s*(정상|에스컬레이션)\s*$", output, re.MULTILINE)
    if not v:
        return None
    r = re.search(r"^REASON:\s*(.+)$", output, re.MULTILINE)
    return {"verdict": v.group(1), "reason": (r.group(1).strip() if r else "")}


def investigate(partner, diff, timeout=180):
    prompt = build_prompt(partner, diff)
    try:
        proc = subprocess.run(
            [HERMES_BIN, "-z", prompt, "--yolo"],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"partner": partner, "diff": diff, "verdict": "조사실패", "reason": "타임아웃"}
    parsed = parse_verdict(proc.stdout)
    if parsed is None:
        return {
            "partner": partner, "diff": diff,
            "verdict": "조사실패", "reason": "형식 파싱 실패",
        }
    parsed.update({"partner": partner, "diff": diff})
    return parsed


def main():
    partner = sys.argv[1]
    diff = int(sys.argv[2])
    print(json.dumps(investigate(partner, diff), ensure_ascii=False))


if __name__ == "__main__":
    main()
