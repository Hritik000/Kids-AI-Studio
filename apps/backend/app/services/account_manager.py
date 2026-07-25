import uuid
from typing import Dict, List, Optional
from app.models.distribution import ConnectedAccount

# In-memory storage for connected accounts
connected_accounts_db: Dict[str, ConnectedAccount] = {}

class AccountManagerService:
    @staticmethod
    def initialize_default_accounts():
        if not connected_accounts_db:
            acc1 = ConnectedAccount(
                account_id="acc_yt_001",
                platform="YouTube",
                display_name="KidsAI Studio Channel",
                channel_name="KidsAIStudioOfficial",
                avatar_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80",
                connection_status="CONNECTED"
            )
            acc2 = ConnectedAccount(
                account_id="acc_tt_002",
                platform="TikTok",
                display_name="KidsAI Shorts",
                channel_name="kidsaistudio",
                avatar_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80",
                connection_status="CONNECTED"
            )
            connected_accounts_db[acc1.account_id] = acc1
            connected_accounts_db[acc2.account_id] = acc2

    @staticmethod
    def list_accounts() -> List[ConnectedAccount]:
        AccountManagerService.initialize_default_accounts()
        return list(connected_accounts_db.values())

    @staticmethod
    def connect_account(platform: str, channel_name: str) -> ConnectedAccount:
        acc = ConnectedAccount(
            account_id=f"acc_{platform.lower()[:3]}_{uuid.uuid4().hex[:6]}",
            platform=platform,
            display_name=f"{channel_name} Channel",
            channel_name=channel_name,
            avatar_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80",
            connection_status="CONNECTED"
        )
        connected_accounts_db[acc.account_id] = acc
        return acc

    @staticmethod
    def disconnect_account(account_id: str) -> bool:
        if account_id in connected_accounts_db:
            del connected_accounts_db[account_id]
            return True
        return False
