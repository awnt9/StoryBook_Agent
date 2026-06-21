from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.api_key_crypto import ApiKeyCipher
from app.core.config import settings
from app.repositories.api_key_repository import ApiKeyRepository
from app.schemas.api_key import ApiKeyRead, UserApiKey


class ApiKeyService:
    def __init__(self, db: Session):
        self.repository = ApiKeyRepository(db)
        self.cipher = ApiKeyCipher(
            settings.api_key_encryption_key.get_secret_value()
        )

    def list(self, user_id: int) -> list[ApiKeyRead]:
        return [
            self._to_read(api_key)
            for api_key in self.repository.list_by_user(user_id)
        ]

    def create(
        self,
        *,
        user_id: int,
        label: str,
        provider: str,
        api_key: str,
    ) -> ApiKeyRead:
        clean_label = label.strip()
        clean_provider = provider.strip().lower()
        clean_api_key = api_key.strip()

        if not clean_label or not clean_provider or not clean_api_key:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Label, provider and API key cannot be blank",
            )

        stored_key = self.repository.create(
            user_id=user_id,
            label=clean_label,
            provider=clean_provider,
            encrypted_key=self.cipher.encrypt(clean_api_key),
            last_four=clean_api_key[-4:],
        )
        return self._to_read(stored_key)

    def reveal(self, *, user_id: int, api_key_id: int) -> str:
        api_key = self._get_owned(user_id=user_id, api_key_id=api_key_id)
        try:
            return self.cipher.decrypt(api_key.encrypted_key)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The stored API key cannot be decrypted",
            ) from error

    def select(self, *, user_id: int, api_key_id: int) -> ApiKeyRead:
        api_key = self._get_owned(user_id=user_id, api_key_id=api_key_id)
        return self._to_read(self.repository.select(api_key))

    def delete(self, *, user_id: int, api_key_id: int) -> None:
        api_key = self._get_owned(user_id=user_id, api_key_id=api_key_id)
        self.repository.delete(api_key)

    def get_selected_plaintext(self, user_id: int) -> str:
        selected = next(
            (
                api_key
                for api_key in self.repository.list_by_user(user_id)
                if api_key.is_selected
            ),
            None,
        )
        if selected is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No API key is selected",
            )
        if selected.id is None:
            raise RuntimeError("Selected API key has no database ID")
        return self.reveal(user_id=user_id, api_key_id=selected.id)

    def _get_owned(self, *, user_id: int, api_key_id: int) -> UserApiKey:
        api_key = self.repository.get_owned(api_key_id, user_id)
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found",
            )
        return api_key

    @staticmethod
    def _to_read(api_key: UserApiKey) -> ApiKeyRead:
        if api_key.id is None:
            raise RuntimeError("Stored API key has no database ID")
        return ApiKeyRead(
            id=api_key.id,
            label=api_key.label,
            provider=api_key.provider,
            masked_key=f"••••••••{api_key.last_four}",
            is_selected=api_key.is_selected,
            created_at=api_key.created_at,
        )
