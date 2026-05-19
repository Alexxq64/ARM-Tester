# db/analytics/slow_tests.py
def get_slow_tests(db, threshold_sec=5.0, limit=5):
    runs = db.get_test_runs(1)
    if not runs:
        return []
    
    last_run_id = runs[0][0]
    results = db.get_test_results_by_run(last_run_id)
    
    slow = []
    for r in results:
        _, _, test_id, _, _, status, exec_time, _ = r
        if exec_time and exec_time > threshold_sec:
            test = db.get_test_case_by_id(test_id)
            if test:
                _, name, group, _, _ = test
                slow.append({
                    "test_id": test_id,
                    "test_name": name,
                    "group": group or "Без группы",
                    "execution_time": exec_time,
                    "status": status
                })
    
    slow.sort(key=lambda x: x["execution_time"], reverse=True)
    return slow[:limit]