from cryptography.fernet import Fernet, InvalidToken


class ApiKeyCipher:
    def __init__(self, encryption_key: str):
        try:
            self._fernet = Fernet(encryption_key.encode("utf-8"))
        except (TypeError, ValueError) as error:
            raise ValueError(
                "API_KEY_ENCRYPTION_KEY must be a valid Fernet key"
            ) from error

    def encrypt(self, api_key: str) -> str:
        return self._fernet.encrypt(api_key.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_key: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_key.encode("utf-8")).decode("utf-8")
        except InvalidToken as error:
            raise ValueError("Unable to decrypt the stored API key") from error
