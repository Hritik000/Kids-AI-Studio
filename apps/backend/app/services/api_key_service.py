import uuid
from typing import Dict, List
from app.models.saas import APIKeyItem

api_keys_db: Dict[str, APIKeyItem] = {}

class APIKeyService:
    @staticmethod
    def list_api_keys(user_id: str) -> List[APIKeyItem]:
        return [k for k in api_keys_db.values() if k.user_id == user_id]

    @staticmethod
    def create_api_key(user_id: str, name: str) -> APIKeyItem:
        key = APIKeyItem(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            name=name,
            secret_key=f"kAI_live_{uuid.uuid4().hex[:16]}",
            scopes=["read", "write"]
        )
        api_keys_db[key.key_id] = key
        return key

    @staticmethod
    def revoke_api_key(user_id: str, key_id: str) -> bool:
        if key_id in api_keys_db and api_keys_db[key_id].user_id == user_id:
            del api_keys_db[key_id]
            return True
        return False
