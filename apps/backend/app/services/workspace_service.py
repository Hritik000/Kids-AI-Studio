import uuid
from typing import Dict, List
from app.models.saas import Workspace, WorkspaceMember

workspaces_db: Dict[str, Workspace] = {}
workspace_members_db: Dict[str, List[WorkspaceMember]] = {}

class WorkspaceService:
    @staticmethod
    def initialize_user_workspace(user_id: str) -> Workspace:
        user_ws = [ws for ws in workspaces_db.values() if ws.owner_id == user_id]
        if user_ws:
            return user_ws[0]

        ws = Workspace(
            workspace_id=f"ws_{uuid.uuid4().hex[:8]}",
            name="Personal Workspace",
            owner_id=user_id,
            type="PERSONAL"
        )
        workspaces_db[ws.workspace_id] = ws

        member = WorkspaceMember(
            member_id=f"mem_{uuid.uuid4().hex[:6]}",
            workspace_id=ws.workspace_id,
            user_id=user_id,
            role="OWNER"
        )
        workspace_members_db[ws.workspace_id] = [member]
        return ws

    @staticmethod
    def list_user_workspaces(user_id: str) -> List[Workspace]:
        WorkspaceService.initialize_user_workspace(user_id)
        return [ws for ws in workspaces_db.values() if ws.owner_id == user_id]

    @staticmethod
    def create_workspace(user_id: str, name: str, ws_type: str = "TEAM") -> Workspace:
        ws = Workspace(
            workspace_id=f"ws_{uuid.uuid4().hex[:8]}",
            name=name,
            owner_id=user_id,
            type=ws_type
        )
        workspaces_db[ws.workspace_id] = ws
        member = WorkspaceMember(
            member_id=f"mem_{uuid.uuid4().hex[:6]}",
            workspace_id=ws.workspace_id,
            user_id=user_id,
            role="OWNER"
        )
        workspace_members_db[ws.workspace_id] = [member]
        return ws
