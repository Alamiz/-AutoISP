class TokenStorage:
    _instance = None
    _token = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenStorage, cls).__new__(cls)
        return cls._instance

    def set_token(self, token: str):
        self._token = token

    def get_token(self) -> str:
        return self._token

# Global instance
token_storage = TokenStorage()