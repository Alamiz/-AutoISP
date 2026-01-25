from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Account(BaseModel):
    """
    Represents an account with all its properties.
    """
    id: str
    email: str
    password: Optional[str] = None
    provider: Optional[str] = None
    proxy_settings: Optional[Dict[str, Any]] = None
    type: str = "desktop"
    status: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    
    # Allow extra fields if the API returns more data
    class Config:
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure password is set from credentials if not provided directly
        if not self.password and self.credentials and "password" in self.credentials:
            self.password = self.credentials["password"]