"""정산 대사 HTTP 서비스 — n8n이 HTTP Request 노드로 호출한다.

엔드포인트:
  GET /health              → {"status": "ok"}
  GET /reconcile           → 불일치 건 목록 [{"partner","order_sum","settled","diff"}, ...]
  GET /investigate?partner=거래처C&diff=-6 → 조사 판정 {"partner","diff","verdict","reason"}
  GET /run                 → 전체 파이프라인 실행(리포트 저장+디스코드 게시)
                             {"results","summary","report_path","posted"}
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
import investigate
import load_to_sqlite
import reconcile
import run_all

PORT = 8787


def parse_investigate_params(query_string):
    q = parse_qs(query_string)
    partner = q.get("partner", [""])[0]
    diff = int(q.get("diff", ["0"])[0])
    return partner, diff


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path == "/health":
                self._send(200, {"status": "ok"})
            elif u.path == "/reconcile":
                self._send(200, reconcile.reconcile())
            elif u.path == "/investigate":
                partner, diff = parse_investigate_params(u.query)
                self._send(200, investigate.investigate(partner, diff))
            elif u.path == "/run":
                self._send(200, run_all.run_pipeline())
            else:
                self._send(404, {"error": "not found", "path": u.path})
        except Exception as e:
            self._send(500, {"error": str(e)})

    def log_message(self, *args):
        pass  # 접근 로그 억제


def main():
    load_to_sqlite.main()  # 기동 시 DB 준비 (한 번만)
    print(f"정산 대사 서비스 http://127.0.0.1:{PORT}  (/health /reconcile /investigate /run)")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
