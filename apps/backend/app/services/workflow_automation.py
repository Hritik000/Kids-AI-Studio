import uuid
from typing import Dict, List
from app.models.copilot import WorkflowAutomationItem

workflows_db: Dict[str, WorkflowAutomationItem] = {}

class WorkflowAutomationService:
    @staticmethod
    def initialize_default_workflows():
        if not workflows_db:
            wf1 = WorkflowAutomationItem(
                workflow_id="wf_auto_001",
                name="Auto-Generate SEO Package on Render Complete",
                trigger_event="RENDER_COMPLETED",
                actions=["generate_seo_package", "generate_thumbnails_abcd"],
                is_active=True
            )
            wf2 = WorkflowAutomationItem(
                workflow_id="wf_auto_002",
                name="Auto-Schedule YouTube Release on SEO Approval",
                trigger_event="SEO_APPROVED",
                actions=["schedule_youtube_upload"],
                is_active=True
            )
            workflows_db[wf1.workflow_id] = wf1
            workflows_db[wf2.workflow_id] = wf2

    @staticmethod
    def list_workflows() -> List[WorkflowAutomationItem]:
        WorkflowAutomationService.initialize_default_workflows()
        return list(workflows_db.values())

    @staticmethod
    def create_workflow(name: str, trigger_event: str, actions: List[str]) -> WorkflowAutomationItem:
        wf = WorkflowAutomationItem(
            workflow_id=f"wf_{uuid.uuid4().hex[:6]}",
            name=name,
            trigger_event=trigger_event,
            actions=actions,
            is_active=True
        )
        workflows_db[wf.workflow_id] = wf
        return wf
