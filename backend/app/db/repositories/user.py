from sqlalchemy.orm import Session
from typing import Optional

from app.db.repositories.base import BaseRepository
from app.db.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
