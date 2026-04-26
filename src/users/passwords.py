import bcrypt


class PasswordsHelper():
    """Класс вспоомгательных функций для работы с паролями."""

    def password_hashing(self, password: str) -> str:
        """Хэшируем переданный пользователем пароль."""
        password_bytes = password.encode('utf-8')
        password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return password_hash.decode('utf-8')

    def password_validation(self, password_provided: str, password_hash_stored: str) -> bool:
        """Валидация переданного пользователем пароля."""
        return bcrypt.checkpw(password_provided.encode('utf-8'), password_hash_stored.encode('utf-8'))


passwords = PasswordsHelper()
