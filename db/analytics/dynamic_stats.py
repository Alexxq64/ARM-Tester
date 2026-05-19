# db/analytics/dynamic_stats.py
def get_dynamic_stats(db, runs_count=10):
    runs = db.get_test_runs(1)
    if len(runs) < 2:
        return {
            "trend": "stable",
            "trend_percent": 0.0,
            "last_rate": 0.0,
            "previous_rate": 0.0,
            "run_ids": [],
            "pass_rates": []
        }
    
    runs = runs[:runs_count]
    runs.reverse()
    
    run_ids = []
    rates = []
    
    for run in runs:
        run_id, _, _, _ = run
        results = db.get_test_results_by_run(run_id)
        total = len(results)
        if total == 0:
            continue
        passed = sum(1 for r in results if r[5] == "passed")
        rates.append(passed / total * 100)
        run_ids.append(run_id)
    
    if len(rates) < 2:
        return {
            "trend": "stable",
            "trend_percent": 0.0,
            "last_rate": rates[-1] if rates else 0.0,
            "previous_rate": 0.0,
            "run_ids": run_ids,
            "pass_rates": rates
        }
    
    last = rates[-1]
    prev = rates[-2]
    diff = last - prev
    
    if diff > 5:
        trend = "up"
    elif diff < -5:
        trend = "down"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "trend_percent": diff,
        "last_rate": last,
        "previous_rate": prev,
        "run_ids": run_ids,
        "pass_rates": rates
    }