from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from database import init_db, get_db, Branch, Checkpoint
from database import User


init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(username: str, passw: str, db: Session = Depends(get_db)):
    new_user = User(username=username, password=passw)
    db.add(new_user)
    db.commit()
    return {"status": "Юзер создан!"} 

@app.get("/data/{user_id}")
def get_data(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Юзер не найден")
        
    branches = db.query(Branch).all() 
    return {
        "username": user.username,
        "xp": user.xp, 
        "level": (user.xp // 500) + 1, 
        "branches": branches
    }

@app.post("/add_branch")
def add_branch(title: str, db: Session = Depends(get_db)):
    new_branch = Branch(title=title)
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return {"status": "ok", "id": new_branch.id}

@app.post("/add_cp/{branch_id}")
def add_checkpoint(branch_id: int, name: str, diff: str, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Ветка не найдена")
    
    new_cp = Checkpoint(name=name, difficulty=diff, branch_id=branch_id)
    db.add(new_cp)
    db.commit()
    db.refresh(new_cp)
    return new_cp

@app.post("/complete/{cp_id}")
def complete_task(cp_id: int, user_id: int, db: Session = Depends(get_db)):
    cp = db.query(Checkpoint).filter(Checkpoint.id == cp_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if cp and user and not cp.done:
        cp.done = True
        rewards = {"easy": 10, "medium": 50, "hard": 100}
        user.xp += rewards.get(cp.difficulty, 0)
        
        db.commit()
        return {"new_xp": user.xp, "status": "Задание выполнено!"}
    return {"error": "Ошибка: либо задача уже сделана, либо ппользователь не найден"}


@app.delete("/delete_branch/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Ветка не найдена")
    
    db.delete(branch)
    db.commit()
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

