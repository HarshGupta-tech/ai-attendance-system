"""Authentication service with JWT token management."""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, hash_password, create_access_token
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, username: str, password: str, ip_address: str = "unknown") -> dict:
        """Authenticate user by username/email and password. Returns token dict."""
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        if not user or not verify_password(password, user.password_hash):
            # Log failed attempt
            audit = AuditService(self.db)
            audit.log(
                user_id=None, action="login_failed",
                resource_type="auth", details=f"Failed login for: {username}",
                ip_address=ip_address
            )
            raise ValueError("Invalid username or password")
        if not user.is_active:
            raise ValueError("Account is disabled")

        # Create token
        token = self.create_token(user)

        # Audit log
        audit = AuditService(self.db)
        audit.log(
            user_id=user.id, action="login",
            resource_type="auth", details=f"User logged in",
            ip_address=ip_address
        )
        return token

    def create_token(self, user: User) -> dict:
        """Create JWT token for user."""
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
            }
        }

    def logout(self, user_id: int, ip_address: str = "unknown"):
        """Log logout event."""
        audit = AuditService(self.db)
        audit.log(
            user_id=user_id, action="logout",
            resource_type="auth", details="User logged out",
            ip_address=ip_address
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True
