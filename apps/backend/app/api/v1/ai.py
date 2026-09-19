import time
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.project import Project, ProjectStatus, APIResponse, APIError, Scene
from app.schemas.auth import UserProfile
from app.core.security import get_current_user
from app.api.v1.projects import projects_db
from app.core.db import (
    plans_db,
    stories_db,
    storyboards_db,
    characters_db,
    images_db,
    animations_db,
    audios_db,
    music_mixes_db,
    timelines_db,
    renders_db,
    publishing_db
)
from app.services.director import DirectorAgentService
from app.services.story import StoryAgentService
from app.services.storyboard import StoryboardAgentService
from app.services.character import CharacterEngineService
from app.services.image_generator import ImagePipelineService
from app.services.animation_generator import AnimationPipelineService
from app.services.voice_service import VoicePipelineService
from app.services.music_service import MusicPipelineService
from app.services.timeline_builder import TimelineBuilderService
from app.services.ffmpeg_renderer import FFmpegRenderService
from app.services.thumbnail_planner import ThumbnailPlannerService
from app.services.seo_agent import SEOAgentService

router = APIRouter()

logger = logging.getLogger("kidsai.ai_pipeline")
logger.setLevel(logging.INFO)

director_service = DirectorAgentService()
story_service = StoryAgentService()
storyboard_service = StoryboardAgentService()
image_service = ImagePipelineService()
animation_service = AnimationPipelineService()
voice_service = VoicePipelineService()
music_service = MusicPipelineService()

@router.post("/projects/{project_id}/generate-plan", response_model=APIResponse[Dict[str, Any]])
async def generate_production_plan(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    
    try:
        plan = await director_service.generate_production_plan(
            project_id=project.id,
            topic=project.prompt,
            target_age_group=project.target_age_group,
            language=project.language,
            video_length=project.video_length,
            aspect_ratio=project.aspect_ratio,
            video_style=project.video_style
        )
        
        plans_db[project_id] = plan
        project.status = ProjectStatus.PLANNING
        projects_db[project_id] = project

        return APIResponse(success=True, data=plan)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="PLAN_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/generate-story", response_model=APIResponse[Dict[str, Any]])
async def generate_story(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    
    plan = plans_db.get(project_id)
    if not plan:
        plan = await director_service.generate_production_plan(
            project_id=project.id,
            topic=project.prompt,
            target_age_group=project.target_age_group,
            language=project.language,
            video_length=project.video_length,
            aspect_ratio=project.aspect_ratio,
            video_style=project.video_style
        )
        plans_db[project_id] = plan

    try:
        story = await story_service.generate_story_script(production_plan=plan)
        stories_db[project_id] = story
        
        mapped_scenes = []
        for s in story.get("scenes", []):
            mapped_scenes.append(
                Scene(
                    scene_number=s.get("scene_number", 1),
                    narration_text=s.get("narration_text", ""),
                    visual_prompt=s.get("visual_description", ""),
                    duration_seconds=s.get("estimated_duration", 3.0)
                )
            )
        
        project.title = story.get("story_title", project.title)
        project.description = story.get("story_summary", project.description)
        project.scenes = mapped_scenes
        project.status = ProjectStatus.STORY_READY
        projects_db[project_id] = project

        return APIResponse(success=True, data=story)
    except Exception as e:
        return APIResponse(
            success=False,
            error=APIError(code="STORY_GENERATION_FAILED", message=str(e))
        )

@router.post("/projects/{project_id}/generate-full-pipeline", response_model=APIResponse[Dict[str, Any]])
async def generate_full_pipeline(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Autonomous End-to-End Pipeline Execution:
    Prompt -> Plan -> Story -> Storyboard -> Characters -> Prompts -> Images -> Animations -> Voice -> Music -> FFmpeg Render -> Publishing Package
    """
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    total_start_time = time.time()
    timing_metrics: Dict[str, float] = {}

    try:
        # Step 1: Director Plan
        logger.info(f"Pipeline Started for Project {project_id}: Stage 1 (Director Plan)")
        t0 = time.time()
        plan = await director_service.generate_production_plan(
            project_id=project.id,
            topic=project.prompt,
            target_age_group=project.target_age_group,
            language=project.language,
            video_length=project.video_length,
            aspect_ratio=project.aspect_ratio,
            video_style=project.video_style
        )
        plans_db[project_id] = plan
        timing_metrics["stage_1_plan_sec"] = round(time.time() - t0, 3)

        # Step 2: Story Script
        logger.info(f"Pipeline Stage 2: Story Script Generation")
        t0 = time.time()
        story = await story_service.generate_story_script(production_plan=plan)
        stories_db[project_id] = story
        timing_metrics["stage_2_story_sec"] = round(time.time() - t0, 3)

        # Step 3: Storyboard
        logger.info(f"Pipeline Stage 3: Storyboard Generation")
        t0 = time.time()
        sb = await storyboard_service.generate_storyboard(
            project_id=project_id,
            story_script=story,
            production_plan=plan
        )
        storyboards_db[project_id] = sb
        timing_metrics["stage_3_storyboard_sec"] = round(time.time() - t0, 3)

        # Step 4: Characters Engine
        logger.info(f"Pipeline Stage 4: Character Profile Extraction")
        t0 = time.time()
        chars = CharacterEngineService.extract_and_generate_profiles(
            project_id=project_id,
            story_script=story,
            video_style=project.video_style
        )
        characters_db[project_id] = chars
        timing_metrics["stage_4_characters_sec"] = round(time.time() - t0, 3)

        # Step 5: Images Generation (FLUX 3D)
        logger.info(f"Pipeline Stage 5: Image Prompts & FLUX Scene Rendering")
        t0 = time.time()
        generated_imgs = await image_service.generate_all_scene_images(
            project_id=project_id,
            storyboard=sb,
            characters=chars
        )
        images_db[project_id] = generated_imgs
        timing_metrics["stage_5_images_sec"] = round(time.time() - t0, 3)

        # Step 6: Animation Clips Generation (Wan 2.2)
        logger.info(f"Pipeline Stage 6: Motion Planning & Wan 2.2 Animation Clips")
        t0 = time.time()
        generated_anims = await animation_service.generate_all_scene_animations(
            project_id=project_id,
            storyboard=sb,
            scene_images=generated_imgs,
            characters=chars
        )
        animations_db[project_id] = generated_anims
        timing_metrics["stage_6_animations_sec"] = round(time.time() - t0, 3)

        # Step 7: Voice Narration & Lip Sync (Kokoro TTS)
        logger.info(f"Pipeline Stage 7: Kokoro Voice Narration & Lip Sync Visemes")
        t0 = time.time()
        generated_voices = await voice_service.generate_all_scene_voices(
            project_id=project_id,
            storyboard=sb,
            voice_name=project.voice,
            language=project.language
        )
        audios_db[project_id] = generated_voices
        timing_metrics["stage_7_voices_sec"] = round(time.time() - t0, 3)

        # Step 8: Audio Mixing & Mastering (Stable Audio)
        logger.info(f"Pipeline Stage 8: Stable Audio Music & -14.0 LUFS Audio Mixing")
        t0 = time.time()
        generated_mixes = await music_service.generate_all_scene_music_mixes(
            project_id=project_id,
            storyboard=sb,
            production_plan=plan
        )
        music_mixes_db[project_id] = generated_mixes
        timing_metrics["stage_8_music_sec"] = round(time.time() - t0, 3)

        # Step 9: Timeline & FFmpeg Video Render
        logger.info(f"Pipeline Stage 9: Timeline Compilation & FFmpeg MP4 Render")
        t0 = time.time()
        timeline = TimelineBuilderService.build_timeline(
            project_id=project_id,
            storyboard=sb,
            animations=[a.model_dump() for a in generated_anims],
            voices=[v.model_dump() for v in generated_voices],
            music_mixes=[m.model_dump() for m in generated_mixes],
            aspect_ratio=project.aspect_ratio
        )
        timelines_db[project_id] = timeline
        
        render_task = await FFmpegRenderService.render_video(
            project_id=project_id,
            timeline=timeline,
            resolution="1080p",
            codec="H.264"
        )
        timing_metrics["stage_9_render_sec"] = round(time.time() - t0, 3)

        # Step 10: Publishing Package Generation
        logger.info(f"Pipeline Stage 10: Thumbnail Variants & COPPA SEO Package")
        t0 = time.time()
        thumb_plan = ThumbnailPlannerService.plan_thumbnail_variants(
            storyboard=sb,
            project_title=story.get("story_title", project.title)
        )
        seo_pkg = SEOAgentService.generate_seo_package(
            project_id=project_id,
            project_title=story.get("story_title", project.title),
            prompt=project.prompt,
            story_script=story
        )
        publishing_bundle = {
            "bundle_id": f"pub_{project_id}",
            "project_id": project_id,
            "thumbnails": [t.model_dump() for t in thumb_plan],
            "seo": seo_pkg.model_dump(),
            "status": "GENERATED"
        }
        publishing_db[project_id] = publishing_bundle
        timing_metrics["stage_10_publishing_sec"] = round(time.time() - t0, 3)

        total_duration = round(time.time() - total_start_time, 3)
        timing_metrics["total_pipeline_duration_sec"] = total_duration

        # Update Project Final Status
        project.title = story.get("story_title", project.title)
        project.status = ProjectStatus.COMPLETED
        project.final_video_url = render_task.final_video_url
        project.thumbnail_url = render_task.preview_url
        projects_db[project_id] = project

        logger.info(f"Pipeline Finished Successfully for Project {project_id} in {total_duration}s")

        return APIResponse(
            success=True,
            data={
                "project_id": project_id,
                "status": "COMPLETED",
                "story_title": story.get("story_title"),
                "total_scenes": len(sb.get("scenes", [])),
                "final_video_url": render_task.final_video_url,
                "download_url": render_task.final_video_url,
                "thumbnail_url": render_task.preview_url,
                "timing_metrics": timing_metrics
            }
        )

    except Exception as e:
        logger.error(f"Pipeline Failed for Project {project_id}: {str(e)}", exc_info=True)
        return APIResponse(
            success=False,
            error=APIError(code="PIPELINE_EXECUTION_FAILED", message=str(e))
        )

@router.get("/projects/{project_id}/plan", response_model=APIResponse[Dict[str, Any]])
async def get_production_plan(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    plan = plans_db.get(project_id)
    if not plan:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Production plan has not been generated yet")
        )

    return APIResponse(success=True, data=plan)

@router.get("/projects/{project_id}/story", response_model=APIResponse[Dict[str, Any]])
async def get_story_script(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    story = stories_db.get(project_id)
    if not story:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Story script has not been generated yet")
        )

    return APIResponse(success=True, data=story)

@router.post("/projects/{project_id}/regenerate-story", response_model=APIResponse[Dict[str, Any]])
async def regenerate_story(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    return await generate_story(project_id=project_id, current_user=current_user)

@router.get("/projects/{project_id}/pipeline-status", response_model=APIResponse[Dict[str, Any]])
async def get_pipeline_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    if project_id not in projects_db:
        return APIResponse(
            success=False,
            error=APIError(code="NOT_FOUND", message="Project not found")
        )

    project = projects_db[project_id]
    has_plan = project_id in plans_db
    has_story = project_id in stories_db
    has_sb = project_id in storyboards_db
    has_render = project_id in renders_db

    return APIResponse(
        success=True,
        data={
            "project_id": project.id,
            "status": project.status,
            "has_production_plan": has_plan,
            "has_story_script": has_story,
            "has_storyboard": has_sb,
            "has_render": has_render,
            "current_step": 10 if has_render else 3 if has_sb else 2 if has_story else 1,
            "total_steps": 10
        }
    )
