import re

def name_check(name: str):
    name = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9]+", name):
        return False
    return True