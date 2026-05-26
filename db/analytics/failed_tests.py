# db/analytics/failed_tests.py
def get_failed_tests_last_run(db, limit=5):
    runs = db.get_test_runs(1)
    if not runs:
        return []
    
    last_run_id = runs[0][0]
    results = db.get_test_results_by_run(last_run_id)
    
    failed = []
    for r in results:
        # result_id, run_id, test_id, func_name, file_path, status, exec_time, error_msg
        _, _, test_id, _, _, status, exec_time, error_msg = r
        if status in ("failed", "error"):
            test = db.get_test_case_by_id(test_id)
            if test:
                name = test.get('name', '')
                group = test.get('group_name', '')
                failed.append({
                    "test_id": test_id,
                    "test_name": name,
                    "group": group or "Без группы",
                    "status": status,
                    "execution_time": exec_time,
                    "error_message": (error_msg[:200] if error_msg else "Нет сообщения")
                })
    return failed[:limit]