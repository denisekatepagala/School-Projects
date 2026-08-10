from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import engine
from app.models.models import User

router = APIRouter(prefix="/users", tags=["Users"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/", response_model=list[User])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return session.get(User, user_id)

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        return {"error": "User not found"}
    for key, value in updated_user.dict(exclude_unset=True).items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        return {"error": "User not found"}
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
