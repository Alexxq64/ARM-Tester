from db.database import Database

def load_tests(db, project_id):
    """Загружает тесты из переданного Database объекта"""
    return list(db.get_test_cases(project_id))

def get_groups(tests):
    return sorted(set(t[2] for t in tests if t[2]))