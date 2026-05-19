from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from db.database import Database
from gui.add_project_dialog import AddProjectDialog
from gui.add_edit_test_dialog import AddEditTestDialog
from gui.runs_history_window import RunsHistoryWindow
from gui.analytics_chart import AnalyticsChartWindow
from gui.test_runner import TestRunner
from project_context import ProjectContext


class ActionsHandler:
    def __init__(self, parent, db, table, load_data_callback):
        self.parent = parent
        self.db = db
        self.table = table
        self.load_data = load_data_callback
        self.current_context = None
    
    def add_project(self):
        dialog = AddProjectDialog(self.parent)
        if dialog.exec() == AddProjectDialog.DialogCode.Accepted:
            name, desc, root_path = dialog.get_data()
            if not name:
                QMessageBox.warning(self.parent, "Ошибка", "Название проекта не может быть пустым.")
                return
            if not root_path:
                QMessageBox.warning(self.parent, "Ошибка", "Выберите папку проекта.")
                return
            
            context = ProjectContext(Path(root_path))
            context.ensure_dirs()
            
            self.db.add_project(name, desc, root_path)
            self.load_data()
    
    def edit_project(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для редактирования.")
            return
        
        project_name = selected.get("project_name")
        projects = self.db.get_projects()
        project_data = None
        for p in projects:
            if p[1] == project_name:
                project_data = p
                break
        
        if not project_data:
            QMessageBox.warning(self.parent, "Ошибка", "Проект не найден.")
            return
        
        dialog = AddProjectDialog(self.parent, edit_mode=True, project_data=project_data)
        if dialog.exec() == AddProjectDialog.DialogCode.Accepted:
            name, desc, root_path = dialog.get_data()
            self.db.update_project(project_data[0], name, desc, root_path)
            
            # Обновляем .arm/ если изменился путь
            if root_path and root_path != project_data[3]:
                context = ProjectContext(Path(root_path))
                context.ensure_dirs()
            
            self.load_data()
    
    def delete_project(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для удаления.")
            return
        
        project_name = selected.get("project_name")
        
        reply = QMessageBox.question(
            self.parent,
            "Подтверждение удаления",
            f"Удалить проект \"{project_name}\"?\nВсе тесты и результаты будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            projects = self.db.get_projects()
            for p in projects:
                if p[1] == project_name:
                    self.db.delete_project(p[0])
                    break
            self.load_data()
    
    def add_test(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для добавления теста.")
            return
        
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        dialog = AddEditTestDialog(self.parent, edit_mode=False)
        if dialog.exec() == AddEditTestDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
            if not local_db_path.exists():
                QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
                return
            
            from db.database import Database
            local_db = Database(str(local_db_path))
            local_db.add_test_case(1, data["name"], data["test_path"], data["group_name"], data["is_active"])
            self.load_data()
    
    def edit_test(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите тест для редактирования.")
            return
        
        test_name = selected.get("test_name")
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db_path.exists():
            QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
            return
        
        from db.database import Database
        local_db = Database(str(local_db_path))
        
        # Находим тест по имени
        tests = local_db.get_test_cases(1)
        test_data = None
        for t in tests:
            if t[1] == test_name:
                test_data = t
                break
        
        if not test_data:
            QMessageBox.warning(self.parent, "Ошибка", "Тест не найден.")
            return
        
        test_info = {
            "test_id": test_data[0],
            "name": test_data[1],
            "group_name": test_data[2],
            "test_path": test_data[3],
            "is_active": test_data[4]
        }
        
        dialog = AddEditTestDialog(self.parent, edit_mode=True, test_data=test_info)
        if dialog.exec() == AddEditTestDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            local_db.update_test_case(test_data[0], new_data["name"], new_data["group_name"], new_data["test_path"], new_data["is_active"])
            self.load_data()
    
    def delete_test(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите тест для удаления.")
            return
        
        test_name = selected.get("test_name")
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        reply = QMessageBox.question(
            self.parent,
            "Подтверждение удаления",
            f"Удалить тест \"{test_name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
            if not local_db_path.exists():
                QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
                return
            
            from db.database import Database
            local_db = Database(str(local_db_path))
            
            tests = local_db.get_test_cases(1)
            for t in tests:
                if t[1] == test_name:
                    local_db.delete_test_case(t[0])
                    break
            
            self.load_data()
    
    def run_selected(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите тест для запуска.")
            return
        
        test_name = selected.get("test_name")
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db_path.exists():
            QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
            return
        
        from db.database import Database
        local_db = Database(str(local_db_path))
        
        # Находим тест
        tests = local_db.get_test_cases(1)
        test_id = None
        test_path = None
        for t in tests:
            if t[1] == test_name:
                test_id = t[0]
                test_path = t[3]
                break
        
        if not test_id:
            QMessageBox.warning(self.parent, "Ошибка", "Тест не найден.")
            return
        
        # Создаём контекст проекта
        context = ProjectContext(Path(root_path))
        context.ensure_dirs()
        
        # Запускаем тест
        TestRunner.run_tests(self.parent, context, 1, [test_id])
        self.load_data()
    
    def run_all(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для запуска всех тестов.")
            return
        
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db_path.exists():
            QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
            return
        
        from db.database import Database
        local_db = Database(str(local_db_path))
        
        # Получаем все активные тесты
        tests = local_db.get_test_cases(1)
        active_ids = [t[0] for t in tests if t[4] == 1]
        
        if not active_ids:
            QMessageBox.information(self.parent, "Информация", "Нет активных тестов.")
            return
        
        context = ProjectContext(Path(root_path))
        context.ensure_dirs()
        
        TestRunner.run_tests(self.parent, context, 1, active_ids)
        self.load_data()
    
    def show_history(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для просмотра истории.")
            return
        
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db_path.exists():
            QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
            return
        
        window = RunsHistoryWindow(1, str(local_db_path), self.parent)
        window.exec()
    
    def show_analytics(self):
        selected = self.table.get_selected_item()
        if not selected:
            QMessageBox.warning(self.parent, "Ошибка", "Выберите проект для просмотра аналитики.")
            return
        
        project_name = selected.get("project_name")
        root_path = self._get_root_path(project_name)
        
        if not root_path:
            QMessageBox.warning(self.parent, "Ошибка", "У проекта нет корневой папки.")
            return
        
        local_db_path = Path(root_path) / ".arm" / "arm_testing.db"
        if not local_db_path.exists():
            QMessageBox.warning(self.parent, "Ошибка", "Локальная БД проекта не найдена.")
            return
        
        window = AnalyticsChartWindow(1, str(local_db_path), self.parent)
        window.exec()
    
    def _get_root_path(self, project_name):
        projects = self.db.get_projects()
        for p in projects:
            if p[1] == project_name:
                return p[3]
        return None