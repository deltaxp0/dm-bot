import json
import os
from colorama import Fore


global db
db = {}

def update_db():
    global db
    with open("db.json", 'w') as file:
        json.dump(db, file, indent=4)
    return db

def reset_db():
    global db
    db={"registry":[]}
    update_db()
    return db

if os.path.exists("db.json"):
    with open("db.json", "r") as file:
        db = json.load(file)
else:
    reset_db()
