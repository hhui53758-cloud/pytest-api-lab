"""检查实际报告与日志中的测试密码和原始令牌。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    contents = []
    for path in [ROOT / "logs" / "api-tests.log", ROOT / "reports" / "report.html"]:
        if not path.is_file():
            raise SystemExit(f"Missing artifact: {path.name}; run scripts/run_tests.py first")
        contents.append(path.read_text(encoding="utf-8"))
    text = "\n".join(contents)
    settings = json.loads((ROOT / "config" / "settings.json").read_text(encoding="utf-8"))
    passwords = [account["password"] for account in settings["accounts"].values()]
    passwords.extend(["WrongPassword!", "AnyPassword!"])
    for password in passwords:
        if password in text:
            raise SystemExit("Found an unredacted demo password")
    if re.search(r"Bearer\s+[A-Za-z0-9_-]{20,}", text):
        raise SystemExit("Found an unredacted bearer token")
    if re.search(r"access_token['\"]\s*:\s*['\"][A-Za-z0-9_-]{20,}", text):
        raise SystemExit("Found an unredacted access token")
    if "[REDACTED]" not in text or "elapsed_ms=" not in text:
        raise SystemExit("Missing expected logging evidence")
    print("PASS: demo passwords and raw tokens absent; redaction and timing evidence present.")


if __name__ == "__main__":
    main()
