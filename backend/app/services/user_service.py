from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import hash_password
from typing import Optional, Tuple, List

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, data: UserCreate) -> User:
        existing = self.db.query(User).filter(
            or_(User.username == data.username, User.email == data.email)
        ).first()
        if existing:
            raise ValueError("Username or email already exists")
            
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            full_name=data.full_name,
            is_active=data.is_active
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_users(self, page: int = 1, per_page: int = 20,
                  role: Optional[str] = None, search: Optional[str] = None) -> Tuple[List[User], int]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
            
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        return users, total
    
    def update_user(self, user_id: int, data: UserUpdate) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
            
        update_data = data.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['password_hash'] = hash_password(update_data.pop('password'))
            
        for key, value in update_data.items():
            setattr(user, key, value)
            
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
    
    def toggle_active(self, user_id: int) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        user.is_active = not user.is_active
        self.db.commit()
        self.db.refresh(user)
        return user
