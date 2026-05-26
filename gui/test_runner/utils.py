from pathlib import Path
from PySide6.QtWidgets import QMessageBox


def validate_tests(db, test_ids, project_root):
    """
    Проверяет существование тестов в файловой системе.
    
    Returns:
        tuple: (valid_tests, not_found)
        valid_tests: list of (tid, name, rel_path, full_path, test_params)
        not_found: list of (name, rel_path)
    """
    valid_tests = []
    not_found = []
    
    for tid in test_ids:
        t = db.get_test_case_by_id(tid)
        if not t:
            continue
        
        full_path = project_root / t["test_path"]
        
        if full_path.exists():
            valid_tests.append(
                (tid, t["name"], t["test_path"], str(full_path), t.get("test_params", "{}"))
            )
        else:
            not_found.append(
                (t["name"], t["test_path"])
            )
    
    return valid_tests, not_found


def show_not_found_warning(parent, not_found):
    """Показывает предупреждение о ненайденных тестах"""
    if not not_found:
        return
    
    warn_msg = "Следующие тесты не найдены в файловой системе и не были запущены:\n"
    for name, path in not_found[:5]:
        warn_msg += f"  - {name}: {path}\n"
    if len(not_found) > 5:
        warn_msg += f"  ... и ещё {len(not_found)-5}"
    
    QMessageBox.warning(parent, "Тесты не найдены", warn_msg)