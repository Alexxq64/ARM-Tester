# db/analytics/flaky_tests.py
from collections import defaultdict

def get_flaky_tests(db, runs_count=5, change_threshold=2):
    runs = db.get_test_runs(1)
    if len(runs) < 2:
        return []
    
    runs = runs[:runs_count]
    
    history = defaultdict(list)
    for run in runs:
        run_id = run[0]
        for r in db.get_test_results_by_run(run_id):
            _, _, test_id, _, _, status, _, _ = r
            history[test_id].append(status)
    
    flaky = []
    for test_id, statuses in history.items():
        if len(statuses) < 2:
            continue
        
        changes = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i-1])
        if changes >= change_threshold:
            test = db.get_test_case_by_id(test_id)
            if test:
                name = test.get('name', '')
                group = test.get('group_name', '')
                flaky.append({
                    "test_id": test_id,
                    "test_name": name,
                    "group": group or "Без группы",
                    "statuses": statuses,
                    "change_count": changes,
                    "latest_status": statuses[-1]
                })
    
    flaky.sort(key=lambda x: x["change_count"], reverse=True)
    return flaky[:5]