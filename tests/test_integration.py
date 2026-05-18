"""Интеграционный тест: запуск реального pytest через АРМ во временном проекте"""

import sys
import os
import tempfile
import shutil
import subprocess
from pathlib import Path

# Добавляем корень проекта в PATH для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from db.database import Database


@pytest.fixture
def temp_project():
    """Создаёт временный Python-проект с тестами"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Создаём простой тестовый файл
        tests_dir = project_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
def test_passes():
    assert True == True

def test_fails():
    assert False == True
""")
        
        # Возвращаем структуру, понятную АРМ
        yield {
            "root": project_path,
            "tests_dir": tests_dir,
            "test_file": test_file,
        }


@pytest.fixture
def arm_db():
    """Создаёт временную БД АРМ для теста"""
    db_path = Path(tempfile.NamedTemporaryFile(suffix=".db").name)
    db = Database(str(db_path))
    yield db
    if db_path.exists():
        db_path.unlink()


def test_integration_run_pytest_through_arm(temp_project, arm_db):
    """
    Сквозной тест:
    1. Создать проект в АРМ
    2. Добавить тестовый сценарий
    3. Запустить тест (имитация через прямой вызов pytest, так как TestRunner требует GUI)
    4. Проверить, что результат сохранился в БД
    """
    
    # 1. Создаём проект в БД АРМ
    project_root = str(temp_project["root"])
    project_id = arm_db.add_project("Интеграционный проект", "Для теста")
    
    # Сохраняем root_path (позже добавим колонку, пока заглушка)
    # TODO: после этапа 3 здесь будет root_path
    
    # 2. Добавляем тестовый сценарий
    test_path = str(temp_project["test_file"])
    test_id = arm_db.add_test_case(
        project_id=project_id,
        name="sample test",
        test_path=test_path,
        group_name="smoke",
        is_active=1
    )
    
    # 3. Запускаем pytest напрямую (имитируем TestRunner, но без GUI)
    import subprocess
    import json
    from datetime import datetime
    
    json_file = temp_project["root"] / ".temp_test.json"
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        test_path,
        "--json-report",
        f"--json-report-file={json_file}"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=temp_project["root"],
        capture_output=True,
        text=True
    )
    
    # 4. Парсим JSON-отчёт
    assert json_file.exists()
    
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
    
    # Очистка
    json_file.unlink()
    
    # 5. Сохраняем результаты в БД (имитируем TestRunner)
    run_id = arm_db.add_test_run(project_id, datetime.now().isoformat(), "running")
    
    for test in data.get("tests", []):
        nodeid = test.get("nodeid", "")
        if "::" in nodeid:
            func_name = nodeid.split("::")[-1]
        else:
            func_name = test.get("name", "unknown")
        
        outcome = test.get("outcome", "failed")
        duration = test.get("duration", 0)
        error = test.get("longrepr", "") if outcome == "failed" else ""
        
        arm_db.add_test_result(
            run_id=run_id,
            test_id=test_id,
            test_function_name=func_name,
            test_file_path=test_path,
            status=outcome,
            execution_time=duration,
            error_message=error[:500]
        )
    
    # Обновляем статус запуска
    arm_db.update_test_run(run_id, datetime.now().isoformat(), "passed" if result.returncode == 0 else "failed")
    
    # 6. Проверяем результаты в БД
    results = arm_db.get_test_results_by_run(run_id)
    
    assert len(results) == 2  # Два теста: test_passes и test_fails
    
    # Находим passed и failed
    statuses = [r[2] for r in results]  # r[2] = status
    assert "passed" in statuses
    assert "failed" in statuses
    
    print(f"✅ Интеграционный тест пройден. Run ID: {run_id}")


def test_integration_real_runner_needed():
    """Заглушка для теста с реальным TestRunner (потребуется GUI)"""
    pytest.skip("TestRunner требует QApplication, будет протестирован отдельно")