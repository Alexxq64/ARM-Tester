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
