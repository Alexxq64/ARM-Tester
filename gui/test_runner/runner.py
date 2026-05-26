# gui/test_runner/runner.py
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

from db.database import Database
from gui.test_runner.utils import validate_tests, show_not_found_warning
from gui.test_runner.pytest_executor import PytestExecutor
from gui.test_runner.result_saver import ResultSaver


class TestRunner:
    
    @staticmethod
    def run_tests(parent, context, project_id, test_ids):
        """
        Запускает тесты через pytest в контексте проекта.
        """
        if not context:
            QMessageBox.warning(parent, "Ошибка", "Контекст проекта не задан.")
            return
        
        # Используем БД внутри .arm/
        db = Database(str(context.db_path))
        
        # Проверяем существование тестов (возвращает 5 элементов: tid, name, rel_path, full_path, params)
        valid_tests, not_found = validate_tests(db, test_ids, context.project_root)
        
        if not valid_tests:
            show_not_found_warning(parent, not_found)
            return
        
        # Создаём запись о запуске
        start_time = datetime.now().isoformat()
        run_id = db.add_test_run(project_id, start_time, "running")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        # Запускаем каждый тест
        for tid, test_name, test_rel_path, full_path, test_params in valid_tests:
            test_results = PytestExecutor.run_single_test(
                context.python_path,
                full_path,
                context.project_root,
                test_params
            )
            
            t, p, f = ResultSaver.save_results(
                db, run_id, test_results, tid, test_rel_path
            )
            total_tests += t
            total_passed += p
            total_failed += f
        
        # Обновляем статус запуска
        end_time = datetime.now().isoformat()
        overall_status = "passed" if total_failed == 0 else "failed"
        db.update_test_run(run_id, end_time, overall_status)
        
        # Автоматически генерируем HTML-отчёт
        try:
            from reports.report_generator import ReportGenerator
            reports_dir = context.project_root / "reports" / "generated"
            reports_dir.mkdir(parents=True, exist_ok=True)
            output_path = reports_dir / f"report_run_{run_id}.html"
            ReportGenerator.generate_report(run_id, str(output_path), str(context.db_path))
            db.add_report(run_id, str(output_path), datetime.now().isoformat())
        except Exception as e:
            print(f"Ошибка создания отчёта: {e}")
        
        # Показываем предупреждение о ненайденных тестах
        show_not_found_warning(parent, not_found)
        
        QMessageBox.information(parent, "Запуск завершён", f"Тестов пройдено: {total_passed}, упало: {total_failed}")