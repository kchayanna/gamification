import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "data.json"


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"xp": 0, "branches": []}
    return {"xp": 0, "branches": []}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class Checkpoint(BaseModel):
    id: int
    name: str
    difficulty: str
    done: bool = False

class Branch(BaseModel):
    id: int
    title: str
    checkpoints: List[Checkpoint] = []


@app.get("/data")
def get_data():
    return load_db()

@app.post("/add_branch")
def add_branch(title: str):
    db = load_db()
    new_id = len(db["branches"]) + 1
    db["branches"].append({
        "id": new_id,
        "title": title,
        "checkpoints": []
    })
    save_db(db)
    return {"status": "ok", "id": new_id}

@app.post("/add_cp/{branch_id}")
def add_checkpoint(branch_id: int, name: str, diff: str):
    db = load_db()
    branch = next((b for b in db["branches"] if b["id"] == branch_id), None)
    if branch:
        new_cp = {
            "id": len(branch["checkpoints"]) + 1,
            "name": name,
            "difficulty": diff,
            "done": False
        }
        branch["checkpoints"].append(new_cp)
        save_db(db)
        return new_cp
    return {"error": "Ветка не найдена"}

@app.post("/complete/{branch_id}/{cp_id}")
def complete_checkpoint(branch_id: int, cp_id: int):
    db = load_db()
    branch = next((b for b in db["branches"] if b["id"] == branch_id), None)
    if branch:
        cp = next((c for c in branch["checkpoints"] if c["id"] == cp_id), None)
        if cp and not cp["done"]:
            cp["done"] = True
            rewards = {"easy": 50, "medium": 150, "hard": 300}
            db["xp"] += rewards.get(cp["difficulty"], 0)
            save_db(db)
            return db
    return {"error": "Ошибка выполнения"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

