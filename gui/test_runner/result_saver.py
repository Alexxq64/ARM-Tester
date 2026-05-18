class ResultSaver:
    @staticmethod
    def save_results(db, run_id, test_results, test_id, test_rel_path):
        total = 0
        passed = 0
        failed = 0
        
        for result in test_results:
            func_name, outcome, duration, error = result
            
            db.add_test_result(
                run_id,
                test_id,
                func_name,
                test_rel_path,
                outcome,
                duration,
                error[:500] if error else ""
            )
            total += 1
            if outcome == "passed":
                passed += 1
            else:
                failed += 1
        
        return total, passed, failed