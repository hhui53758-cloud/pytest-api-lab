"""跨平台一键执行并生成独立 HTML 报告。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    (ROOT / "reports").mkdir(exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--html=reports/report.html", "--self-contained-html", *sys.argv[1:]],
        cwd=ROOT,
    )
    raise SystemExit(result.returncode)
