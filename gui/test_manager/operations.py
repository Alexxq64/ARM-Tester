from pathlib import Path
from PySide6.QtWidgets import QMessageBox

from config import PROJECT_ROOT
from gui.add_edit_test_dialog import AddEditTestDialog
from gui.test_runner import TestRunner


def add_test(parent, db, project_id):
    """
    Добавляет тест.
    
    Args:
        parent: родительское окно
        db: Database объект (уже с правильным db_path)
        project_id: ID проекта
    """
    dialog = AddEditTestDialog(parent, edit_mode=False)
    if dialog.exec() != AddEditTestDialog.DialogCode.Accepted:
        return False
    
    data = dialog.get_data()
    path = Path(data["test_path"])
    try:
        rel_path = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        rel_path = data["test_path"]
    
    db.add_test_case(project_id, data["name"], rel_path, data["group_name"], data["is_active"])
    return True


def edit_test(parent, db, test_id):
    """
    Редактирует тест.
    
    Args:
        parent: родительское окно
        db: Database объект (уже с правильным db_path)
        test_id: ID теста
    """
    test_data = db.get_test_case_by_id(test_id)
    if not test_data:
        QMessageBox.warning(parent, "Ошибка", "Тест не найден.")
        return False
    
    dialog = AddEditTestDialog(parent, edit_mode=True, test_data=test_data)
    if dialog.exec() != AddEditTestDialog.DialogCode.Accepted:
        return False
    
    new_data = dialog.get_data()
    db.update_test_case(test_id, new_data["name"], new_data["group_name"], new_data["test_path"], new_data["is_active"])
    return True


def delete_tests(parent, db, test_ids):
    """
    Удаляет тесты.
    
    Args:
        parent: родительское окно
        db: Database объект (уже с правильным db_path)
        test_ids: список ID тестов
    """
    if not test_ids:
        QMessageBox.warning(parent, "Ошибка", "Выберите тест для удаления.")
        return False
    
    reply = QMessageBox.question(
        parent, "Подтверждение",
        f"Удалить выбранные тесты ({len(test_ids)} шт.)?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply != QMessageBox.StandardButton.Yes:
        return False
    
    for tid in test_ids:
        db.delete_test_case(tid)
    return True


def run_tests(parent, context, project_id, test_ids):
    """
    Запускает тесты.
    
    Args:
        parent: родительское окно
        context: ProjectContext (содержит пути и python проекта)
        project_id: ID проекта
        test_ids: список ID тестов
    """
    TestRunner.run_tests(parent, context, project_id, test_ids)