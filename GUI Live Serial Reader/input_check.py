import re

def name_check(name: str):
    name = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9 ()/]+", name):
        return False
    return True

def label_check(label: str):
    label = label.strip()
    if not re.fullmatch(r"[A-Za-z0-9 ()/]+", label):
        return False
    return True

def spicy_entry_check(entry: str):
    entry = entry.strip()
    if not re.fullmatch(r"[A-Za-z0-9 (){}^:;|/+*-=<>,.~]+", entry):
        return False
    return True

def int_check(number: str):
    number = number.strip()
    if number.startswith("-") or number.startswith("+") or not number.isdigit():
        return False
    return True