import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QMessageBox

from db.database import Database
from config import PROJECT_ROOT

class TestRunner:
    @staticmethod
    def run_tests(parent, project_id, test_ids):
        db = Database("arm_testing.db")
        
        valid_tests = []
        not_found = []
        
        for tid in test_ids:
            t = db.get_test_case_by_id(tid)
            if not t:
                continue
            full_path = PROJECT_ROOT / t["test_path"]
            if full_path.exists():
                valid_tests.append((tid, t["name"], t["test_path"], full_path))
            else:
                not_found.append((t["name"], t["test_path"]))
        
        if not valid_tests:
            msg = "Ни один тест не найден в файловой системе:\n"
            for name, path in not_found:
                msg += f"  - {name}: {path}\n"
            QMessageBox.warning(parent, "Ошибка запуска", msg)
            return
        
        start_time = datetime.now().isoformat()
        run_id = db.add_test_run(project_id, start_time, "running")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for tid, test_name, test_rel_path, full_path in valid_tests:
            json_file = PROJECT_ROOT / f".temp_result_{tid}.json"
            cmd = [
                "pytest", str(full_path),
                "--json-report", f"--json-report-file={json_file}",
                "--json-report-omit=log,stdout,stderr"
            ]
            
            start = time.time()
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                proc.communicate(timeout=60)
                duration = time.time() - start
                
                if json_file.exists():
                    with open(json_file) as f:
                        data = json.load(f)
                    json_file.unlink()
                    
                    for test in data.get("tests", []):
                        nodeid = test.get("nodeid", "")
                        if "::" in nodeid:
                            func_name = nodeid.split("::")[-1]
                        else:
                            func_name = test.get("name", "unknown")
                        
                        outcome = test.get("outcome", "failed")
                        test_duration = test.get("duration", 0)
                        
                        # Извлекаем сообщение об ошибке из longrepr
                        error = ""
                        if outcome == "failed":
                            error = test.get("longrepr", "")
                            if not error:
                                call_data = test.get("call", {})
                                error = call_data.get("longrepr", "")
                            if not error:
                                error = str(test)
                            if not error:
                                error = "Unknown error"
                        
                        db.add_test_result(run_id, tid, func_name, test_rel_path, outcome, test_duration, error[:500])
                        total_tests += 1
                        if outcome == "passed":
                            total_passed += 1
                        else:
                            total_failed += 1
                else:
                    db.add_test_result(run_id, tid, "", test_rel_path, "failed", 0, "JSON report not created")
                    total_tests += 1
                    total_failed += 1
            except subprocess.TimeoutExpired:
                proc.kill()
                db.add_test_result(run_id, tid, "", test_rel_path, "failed", 60, "Timeout (60s)")
                total_tests += 1
                total_failed += 1
        
        end_time = datetime.now().isoformat()
        overall_status = "passed" if total_failed == 0 else "failed"
        db.update_test_run(run_id, end_time, overall_status)
        
        # Показываем только детальное окно (QMessageBox убран)
        if not_found:
            warn_msg = "Следующие тесты не найдены в файловой системе и не были запущены:\n"
            for name, path in not_found[:5]:
                warn_msg += f"  - {name}: {path}\n"
            if len(not_found) > 5:
                warn_msg += f"  ... и ещё {len(not_found)-5}"
            QMessageBox.warning(parent, "Тесты не найдены", warn_msg)
        
        from gui.run_results_window import RunResultsWindow
        results_window = RunResultsWindow(run_id, parent)
        results_window.exec()