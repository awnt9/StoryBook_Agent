from sqlmodel import Session, select

from app.schemas.api_key import UserApiKey


class ApiKeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int) -> list[UserApiKey]:
        statement = (
            select(UserApiKey)
            .where(UserApiKey.user_id == user_id)
            .order_by(UserApiKey.created_at.desc())
        )
        return list(self.db.exec(statement).all())

    def get_owned(self, api_key_id: int, user_id: int) -> UserApiKey | None:
        statement = select(UserApiKey).where(
            UserApiKey.id == api_key_id,
            UserApiKey.user_id == user_id,
        )
        return self.db.exec(statement).first()

    def create(
        self,
        *,
        user_id: int,
        label: str,
        provider: str,
        encrypted_key: str,
        last_four: str,
    ) -> UserApiKey:
        is_first_key = not self.list_by_user(user_id)
        api_key = UserApiKey(
            user_id=user_id,
            label=label,
            provider=provider,
            encrypted_key=encrypted_key,
            last_four=last_four,
            is_selected=is_first_key,
        )
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    def select(self, api_key: UserApiKey) -> UserApiKey:
        for stored_key in self.list_by_user(api_key.user_id):
            stored_key.is_selected = False
            self.db.add(stored_key)

        self.db.flush()
        api_key.is_selected = True
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    def delete(self, api_key: UserApiKey) -> None:
        user_id = api_key.user_id
        was_selected = api_key.is_selected
        self.db.delete(api_key)
        self.db.flush()

        if was_selected:
            replacement = self.db.exec(
                select(UserApiKey)
                .where(UserApiKey.user_id == user_id)
                .order_by(UserApiKey.created_at.desc())
            ).first()
            if replacement:
                replacement.is_selected = True
                self.db.add(replacement)

        self.db.commit()
