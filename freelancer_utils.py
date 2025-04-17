import json
import os
import random
import time

def is_freelancer_already_contacted(nome, username, link, db_path):
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception:
        db = []
    return any((x.get("link") == link and link) or (x.get("username") == username and username) for x in db)

def save_freelancer_to_db(entry, db_path):
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception:
        db = []
    db.append(entry)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def close_all_chats(page, selectors):
    close_btns = page.query_selector_all(selectors["freelancer_chat_close_button_selector"])
    for btn in close_btns:
        btn.click()
        print("Chat chiusa.")
        time.sleep(random.uniform(0.4, 0.9))
