from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.models.project import APIResponse, APIError
from app.models.copilot import (
    OptimizationReport,
    PerformancePrediction,
    TrendReport,
    WorkflowAutomationItem,
    ContentTemplateItem,
    AIModelConfigItem
)
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.services.creator_copilot import CreatorCopilotService
from app.services.trend_service import TrendService
from app.services.prediction_service import PredictionService
from app.services.workflow_automation import WorkflowAutomationService
from app.services.template_service import TemplateService
from app.services.model_manager import ModelManagerService

router = APIRouter()

class OptimizePromptPayload(BaseModel):
    raw_prompt: str

class CreateWorkflowPayload(BaseModel):
    name: str
    trigger_event: str
    actions: List[str]

class CreateTemplatePayload(BaseModel):
    name: str
    category: str
    description: str
    tags: List[str]
    payload: Dict[str, Any]

class UpdateModelStatusPayload(BaseModel):
    status: str

@router.post("/copilot/analyze-project/{project_id}", response_model=APIResponse[OptimizationReport])
async def analyze_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    report = CreatorCopilotService.analyze_project(
        project_id=project_id,
        title=project.title,
        prompt=project.prompt,
        scene_count=len(project.scenes) if project.scenes else 4
    )
    return APIResponse(success=True, data=report)

@router.post("/copilot/predict-performance/{project_id}", response_model=APIResponse[PerformancePrediction])
async def predict_performance(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    prediction = PredictionService.predict_performance(project_id)
    return APIResponse(success=True, data=prediction)

@router.get("/copilot/trends", response_model=APIResponse[List[TrendReport]])
async def list_trends(
    current_user: UserProfile = Depends(get_current_user)
):
    trends = TrendService.get_trending_topics()
    return APIResponse(success=True, data=trends)

@router.get("/copilot/workflows", response_model=APIResponse[List[WorkflowAutomationItem]])
async def list_workflows(
    current_user: UserProfile = Depends(get_current_user)
):
    workflows = WorkflowAutomationService.list_workflows()
    return APIResponse(success=True, data=workflows)

@router.post("/copilot/workflows", response_model=APIResponse[WorkflowAutomationItem])
async def create_workflow(
    payload: CreateWorkflowPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    wf = WorkflowAutomationService.create_workflow(payload.name, payload.trigger_event, payload.actions)
    return APIResponse(success=True, data=wf)

@router.get("/copilot/templates", response_model=APIResponse[List[ContentTemplateItem]])
async def list_templates(
    current_user: UserProfile = Depends(get_current_user)
):
    templates = TemplateService.list_templates()
    return APIResponse(success=True, data=templates)

@router.post("/copilot/templates", response_model=APIResponse[ContentTemplateItem])
async def create_template(
    payload: CreateTemplatePayload,
    current_user: UserProfile = Depends(get_current_user)
):
    tmpl = TemplateService.create_template(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        tags=payload.tags,
        payload=payload.payload
    )
    return APIResponse(success=True, data=tmpl)

@router.get("/copilot/models", response_model=APIResponse[List[AIModelConfigItem]])
async def list_models(
    current_user: UserProfile = Depends(get_current_user)
):
    models = ModelManagerService.list_models()
    return APIResponse(success=True, data=models)

@router.put("/copilot/models/{model_id}", response_model=APIResponse[AIModelConfigItem])
async def update_model_status(
    model_id: str,
    payload: UpdateModelStatusPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    try:
        updated = ModelManagerService.update_model_status(model_id, payload.status)
        return APIResponse(success=True, data=updated)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="UPDATE_FAILED", message=str(e))
        )

@router.post("/copilot/optimize-prompt", response_model=APIResponse[Dict[str, Any]])
async def optimize_prompt(
    payload: OptimizePromptPayload,
    current_user: UserProfile = Depends(get_current_user)
):
    result = CreatorCopilotService.optimize_prompt(payload.raw_prompt)
    return APIResponse(success=True, data=result)
