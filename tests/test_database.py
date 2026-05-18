import pytest
import os
import sqlite3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from db.database import Database

@pytest.fixture
def temp_db():
    """Фикстура: временная база данных, удаляется после теста"""
    db_path = "test_temp.db"
    db = Database(db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_add_project(temp_db):
    project_id = temp_db.add_project("Тестовый проект", "Описание")
    assert project_id == 1
    projects = temp_db.get_projects()
    assert len(projects) == 1
    assert projects[0][1] == "Тестовый проект"

def test_add_test_case(temp_db):
    temp_db.add_project("Проект")
    project_id = 1
    test_id = temp_db.add_test_case(project_id, "Тест", "test.py", "группа", 1)
    assert test_id == 1
    tests = temp_db.get_test_cases(project_id)
    assert len(tests) == 1
    assert tests[0][1] == "Тест"

def test_get_test_case_by_id(temp_db):
    temp_db.add_project("Проект")
    temp_db.add_test_case(1, "Тест", "test.py", "группа", 1)
    test = temp_db.get_test_case_by_id(1)
    assert test is not None
    assert test["name"] == "Тест"

def test_update_test_case(temp_db):
    temp_db.add_project("Проект")
    temp_db.add_test_case(1, "Старое имя", "test.py", "группа", 1)
    temp_db.update_test_case(1, "Новое имя", "новая группа", "new.py", 0)
    test = temp_db.get_test_case_by_id(1)
    assert test["name"] == "Новое имя"

def test_delete_test_case(temp_db):
    temp_db.add_project("Проект")
    temp_db.add_test_case(1, "Тест", "test.py", "группа", 1)
    temp_db.delete_test_case(1)
    test = temp_db.get_test_case_by_id(1)
    assert test is None

def test_get_test_runs(temp_db):
    """Тест получения списка запусков с фильтрацией по дате"""
    # Создаём проект
    project_id = temp_db.add_project("Проект для теста запусков", "")
    
    # Добавляем два запуска с разными датами
    run1 = temp_db.add_test_run(project_id, "2025-01-01 10:00:00", "passed")
    run2 = temp_db.add_test_run(project_id, "2025-01-02 10:00:00", "failed")
    
    # Получаем все запуски
    runs = temp_db.get_test_runs(project_id)
    assert len(runs) == 2
    
    # Получаем запуски с фильтром по дате (только после 1 января)
    runs_filtered = temp_db.get_test_runs(project_id, date_from="2025-01-02 00:00:00")
    assert len(runs_filtered) == 1
    assert runs_filtered[0][3] == "failed"  # status


def test_delete_test_run(temp_db):
    """Тест удаления запуска (каскадное удаление результатов)"""
    # Создаём проект
    project_id = temp_db.add_project("Проект для теста удаления", "")
    
    # Создаём запуск
    run_id = temp_db.add_test_run(project_id, "2025-01-01 10:00:00", "running")
    
    # Добавляем тест и результат
    test_id = temp_db.add_test_case(project_id, "Тест", "test.py", "", 1)
    temp_db.add_test_result(run_id, test_id, "test_func", "test.py", "passed", 0.5, "")
    
    # Проверяем, что запуск и результат существуют
    results_before = temp_db.get_test_results_by_run(run_id)
    assert len(results_before) == 1
    
    # Удаляем запуск
    temp_db.delete_test_run(run_id)
    
    # Проверяем, что запуск удалён
    runs_after = temp_db.get_test_runs(project_id)
    assert len(runs_after) == 0
    
    # Проверяем, что результаты удалены каскадно
    # (прямая проверка через get_test_results_by_run не работает, т.к. run_id нет)
    # Проверяем через SQL напрямую
    with temp_db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM test_results WHERE run_id = ?", (run_id,))
        count = cur.fetchone()[0]
        assert count == 0


def test_add_and_get_reports(temp_db):
    """Тест добавления и получения отчётов"""
    # Создаём проект и запуск
    project_id = temp_db.add_project("Проект для отчётов", "")
    run_id = temp_db.add_test_run(project_id, "2025-01-01 10:00:00", "passed")
    
    # Добавляем отчёт
    report_id = temp_db.add_report(run_id, "/path/to/report.html", "2025-01-01 12:00:00")
    assert report_id == 1
    
    # Получаем отчёты по запуску
    reports = temp_db.get_reports_by_run(run_id)
    assert len(reports) == 1
    assert reports[0][1] == "/path/to/report.html"  # file_path
    assert reports[0][2] == "2025-01-01 12:00:00"   # created_at
    
    # Добавляем второй отчёт
    temp_db.add_report(run_id, "/path/to/report2.html", "2025-01-01 13:00:00")
    
    reports = temp_db.get_reports_by_run(run_id)
    assert len(reports) == 2


def test_delete_report(temp_db):
    """Тест удаления отчёта"""
    # Создаём проект и запуск
    project_id = temp_db.add_project("Проект для удаления отчётов", "")
    run_id = temp_db.add_test_run(project_id, "2025-01-01 10:00:00", "passed")
    
    # Добавляем отчёт
    report_id = temp_db.add_report(run_id, "/path/to/report.html", "2025-01-01 12:00:00")
    
    # Проверяем, что отчёт есть
    reports_before = temp_db.get_reports_by_run(run_id)
    assert len(reports_before) == 1
    
    # Удаляем отчёт
    temp_db.delete_report(report_id)
    
    # Проверяем, что отчётов нет
    reports_after = temp_db.get_reports_by_run(run_id)
    assert len(reports_after) == 0