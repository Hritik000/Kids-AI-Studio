import uuid
from typing import Dict, List
from app.models.saas import NotificationItem

notifications_db: Dict[str, NotificationItem] = {}

class NotificationService:
    @staticmethod
    def list_notifications(user_id: str) -> List[NotificationItem]:
        user_notes = [n for n in notifications_db.values() if n.user_id == user_id]
        if not user_notes:
            note1 = NotificationItem(
                notification_id=f"ntf_{uuid.uuid4().hex[:6]}",
                user_id=user_id,
                title="Welcome to KidsAI Studio v2.0",
                message="Your Creator Plan is active with 3,500 monthly AI credits.",
                type="SUCCESS"
            )
            notifications_db[note1.notification_id] = note1
            user_notes = [note1]
        return user_notes

    @staticmethod
    def create_notification(user_id: str, title: str, message: str, note_type: str = "INFO") -> NotificationItem:
        note = NotificationItem(
            notification_id=f"ntf_{uuid.uuid4().hex[:6]}",
            user_id=user_id,
            title=title,
            message=message,
            type=note_type
        )
        notifications_db[note.notification_id] = note
        return note

    @staticmethod
    def mark_as_read(user_id: str, notification_id: str) -> bool:
        if notification_id in notifications_db and notifications_db[notification_id].user_id == user_id:
            notifications_db[notification_id].read = True
            return True
        return False
