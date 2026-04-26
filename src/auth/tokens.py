import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from core.config import settings as s
from auth.exceptions import InvalidCredentialsError


class TokenHelper:
    """Класс вспомогательных методов для работы с JWT-токенами."""

    def create_access_token(self, user_id: int) -> str:
        """Формируем JWT access-токен и истечением из настроек."""
        now = datetime.now(timezone.utc)
        payload = {
            'sub': str(user_id),
            'type': 'access',
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=s.ACCESS_TOKEN_EXPIRES_MINUTES)).timestamp()),
        }
        return jwt.encode(payload, key=s.JWT_SECRET, algorithm=s.JWT_ALGORITM)

    def create_refresh_token(self) -> str:
        """Создаем долгоживущий случайный refresh токен (не JWT)."""
        return secrets.token_urlsafe(s.REFRESH_TOKEN_ENTROPY_SIZE)

    def hash_token(self, token: str) -> str:
        """Хэшируем токен через SHA-256."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def decode_token(self, token: str) -> dict:
        """Декодируем JWT и проверяет совпадение типа."""
        token_dict = jwt.decode(jwt=token, key=s.JWT_SECRET, algorithms=[s.JWT_ALGORITM])

        if token_dict.get('type') is None or token_dict['type'] != 'access':
            raise InvalidCredentialsError(s.MESSAGE_AUTHENTICATION_FAILED)

        return token_dict


tokens = TokenHelper()
