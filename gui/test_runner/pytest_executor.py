# gui/test_runner/pytest_executor.py
import subprocess
import time
import os
import json
from pathlib import Path


class PytestExecutor:

    TIMEOUT = 60

    @staticmethod
    def run_single_test(python_path, test_full_path, project_root, test_params="{}"):
        """
        Запускает pytest с --json-report и возвращает список результатов
        по каждому тесту в файле.
        """
        json_file = Path(project_root) / f".temp_result_{os.getpid()}.json"

        cmd = [
            str(python_path),
            "-m",
            "pytest",
            str(test_full_path),
            "--json-report",
            f"--json-report-file={json_file}",
            "--json-report-omit=log,stdout,stderr"
        ]

        env = os.environ.copy()
        env["TEST_PARAMS"] = test_params

        start = time.time()

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=PytestExecutor.TIMEOUT,
                env=env
            )
            duration = time.time() - start

            results = []

            if json_file.exists():
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                json_file.unlink()

                # Обычные тесты
                for test in data.get("tests", []):
                    nodeid = test.get("nodeid", "")
                    if "::" in nodeid:
                        func_name = nodeid.split("::")[-1]
                    else:
                        func_name = test.get("name", "unknown")

                    outcome = test.get("outcome", "failed")
                    test_duration = test.get("duration", 0)

                    error = ""
                    if outcome == "failed":
                        longrepr = test.get("longrepr", "")
                        if isinstance(longrepr, str):
                            error = longrepr
                        elif longrepr:
                            error = json.dumps(longrepr, ensure_ascii=False)
                        if not error:
                            call_data = test.get("call", {})
                            longrepr = call_data.get("longrepr", "")
                            if isinstance(longrepr, str):
                                error = longrepr
                            elif longrepr:
                                error = json.dumps(longrepr, ensure_ascii=False)
                        if not error:
                            error = str(test)
                        if not error:
                            error = "Unknown error"

                    results.append((func_name, outcome, test_duration, error[:500]))

                # Ошибки сбора тестов (ImportError и т.п.)
                if not results:
                    for collector in data.get("collectors", []):
                        if collector.get("outcome") == "failed":
                            error = collector.get("longrepr", "Collection error")
                            if isinstance(error, str):
                                error_msg = error[:500]
                            else:
                                error_msg = json.dumps(error, ensure_ascii=False)[:500]
                            results.append(("[Ошибка сбора]", "failed", 0, error_msg))

            else:
                # JSON не создался — берём из stdout
                stdout = process.stdout + process.stderr
                error = stdout[-500:] if stdout else "JSON report not created"
                results.append(("unknown", "failed", duration, error))

            return results

        except subprocess.TimeoutExpired:
            return [("unknown", "failed", PytestExecutor.TIMEOUT, f"Timeout ({PytestExecutor.TIMEOUT}s)")]