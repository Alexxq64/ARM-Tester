def apply_filter(tests, filter_values):
    name = filter_values.get("name", "").lower()
    group = filter_values.get("group", "Все группы")
    active = filter_values.get("active", "Все")
    
    filtered = tests.copy()
    
    if name:
        filtered = [t for t in filtered if name in t[1].lower()]
    if group != "Все группы":
        filtered = [t for t in filtered if t[2] == group]
    if active == "Активные":
        filtered = [t for t in filtered if t[4] == 1]
    elif active == "Неактивные":
        filtered = [t for t in filtered if t[4] == 0]
    
    return filtered

def sort_tests(tests, col, current_col, current_order):
    if col == current_col:
        current_order = not current_order
    else:
        current_order = False
    
    reverse = current_order
    if col == 0:
        tests.sort(key=lambda x: int(x[0]), reverse=reverse)
    elif col == 1:
        tests.sort(key=lambda x: x[1].lower(), reverse=reverse)
    elif col == 2:
        tests.sort(key=lambda x: (x[2] or "").lower(), reverse=reverse)
    elif col == 3:
        tests.sort(key=lambda x: x[3].lower(), reverse=reverse)
    elif col == 4:
        tests.sort(key=lambda x: x[4], reverse=reverse)
    
    return tests