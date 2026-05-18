import subprocess
import time


class PytestExecutor:

    TIMEOUT = 60

    @staticmethod
    def run_single_test(python_path, test_full_path, project_root):
        cmd = [
            str(python_path),
            "-m",
            "pytest",
            str(test_full_path),
            "-v"
        ]

        start = time.time()

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=PytestExecutor.TIMEOUT
            )
            duration = time.time() - start
            outcome = "passed" if process.returncode == 0 else "failed"
            stdout = process.stdout + process.stderr

            error = stdout[-500:] if process.returncode != 0 and stdout else ""

            return [
                (
                    str(test_full_path),
                    outcome,
                    duration,
                    error
                )
            ]

        except subprocess.TimeoutExpired:
            return [
                (
                    str(test_full_path),
                    "failed",
                    PytestExecutor.TIMEOUT,
                    f"Timeout ({PytestExecutor.TIMEOUT}s)"
                )
            ]