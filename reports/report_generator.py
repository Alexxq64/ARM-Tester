import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from db.database import Database


class ReportGenerator:
    @staticmethod
    def generate_report(run_id, output_path, db_path=None):
        if db_path:
            db = Database(db_path)
        else:
            db = Database("arm_testing.db")
        
        run_info = db.get_run_info(run_id)
        if not run_info:
            raise ValueError(f"Запуск с ID {run_id} не найден")
        
        results_data = db.get_test_results_by_run(run_id)
        
        total_tests = len(results_data)
        passed = sum(1 for r in results_data if r[5] == "passed")
        failed = sum(1 for r in results_data if r[5] == "failed")
        
        results = []
        for r in results_data:
            # r = (result_id, run_id, test_id, func_name, file_path, status, exec_time, error)
            func_name = r[3] if r[3] else ""
            file_path = r[4] if r[4] else ""
            status = r[5]
            error = r[7] if r[7] else ""
            
            results.append({
                "test_name": func_name if func_name else Path(file_path).stem,
                "file_path": file_path,
                "status": status,
                "error_message": error
            })
        
        template_dir = Path(__file__).parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("report_template.html")
        
        html_content = template.render(
            run_id=run_id,
            start_time=run_info["start_time"],
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            results=results,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path