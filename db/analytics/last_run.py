# db/analytics/last_run.py
def get_last_run_info(db):
    runs = db.get_test_runs(1)
    if not runs:
        return None
    
    run_id, start_time, end_time, status = runs[0]
    results = db.get_test_results_by_run(run_id)
    
    total = len(results)
    passed = sum(1 for r in results if r[5] == "passed")
    failed = sum(1 for r in results if r[5] == "failed")
    error = sum(1 for r in results if r[5] == "error")
    skipped = sum(1 for r in results if r[5] == "skipped")
    
    return {
        "run_id": run_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "error": error,
        "skipped": skipped
    }