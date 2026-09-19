"""
Main FFmpeg Video Renderer Orchestrator.
Executes the full end-to-end rendering pipeline:
Assets Validation -> Scene Camera Motion -> Scene Transitions -> Subtitle Overlay -> Audio Mixing & Ducking -> H.264/AAC Encoding -> Thumbnail Generation -> Temp Clean-up.
"""

import os
import time
import uuid
import tempfile
import logging
from typing import List, Optional
from app.services.rendering.models import (
    RenderJobInput, RenderTaskResult, SceneInput, CameraDirection, TransitionType
)
from app.services.rendering.config import rendering_settings
from app.services.rendering.ffmpeg import FFmpegEngine, FFmpegExecutionError
from app.services.rendering.validator import RenderValidatorService
from app.services.rendering.camera import CameraEngine
from app.services.rendering.transitions import TransitionEngine
from app.services.rendering.subtitles import SubtitleEngine
from app.services.rendering.audio import AudioEngine
from app.services.rendering.thumbnail import ThumbnailEngine
from app.services.rendering.downloader import MediaDownloader

logger = logging.getLogger("ffmpeg_renderer")


class FFmpegRenderer:
    @classmethod
    def render(cls, job: RenderJobInput) -> RenderTaskResult:
        """Executes full video render job asynchronously/synchronously."""
        start_time = time.time()
        logs: List[str] = []
        render_id = f"rnd_{job.project_id}_{uuid.uuid4().hex[:6]}"

        logs.append(f"Starting video render pipeline for project {job.project_id} (Render ID: {render_id})")

        # 1. Environment & Asset Validation
        val_env = RenderValidatorService.validate_render_environment()
        if not val_env.is_valid:
            error_msg = f"FFmpeg environment invalid: {'; '.join(val_env.errors)}"
            logs.append(error_msg)
            return RenderTaskResult(
                render_id=render_id,
                project_id=job.project_id,
                timeline_id=job.timeline_id,
                status="FAILED",
                logs=logs
            )

        # 1b. Download and prepare remote media assets
        for sc in job.scenes:
            if sc.image_path:
                try:
                    sc.image_path = MediaDownloader.prepare_media_path(sc.image_path, project_id=job.project_id)
                except Exception as e:
                    error_msg = f"Failed to download or prepare image asset for Scene {sc.scene_number} ({sc.image_path}): {str(e)}"
                    logs.append(error_msg)
                    return RenderTaskResult(
                        render_id=render_id,
                        project_id=job.project_id,
                        timeline_id=job.timeline_id,
                        status="FAILED",
                        logs=logs
                    )

            if sc.narration_path:
                try:
                    sc.narration_path = MediaDownloader.prepare_media_path(sc.narration_path, project_id=job.project_id)
                except Exception as e:
                    error_msg = f"Failed to download or prepare narration asset for Scene {sc.scene_number} ({sc.narration_path}): {str(e)}"
                    logs.append(error_msg)
                    return RenderTaskResult(
                        render_id=render_id,
                        project_id=job.project_id,
                        timeline_id=job.timeline_id,
                        status="FAILED",
                        logs=logs
                    )

        if job.music_path:
            try:
                job.music_path = MediaDownloader.prepare_media_path(job.music_path, project_id=job.project_id)
            except Exception as e:
                error_msg = f"Failed to download or prepare music asset ({job.music_path}): {str(e)}"
                logs.append(error_msg)
                return RenderTaskResult(
                    render_id=render_id,
                    project_id=job.project_id,
                    timeline_id=job.timeline_id,
                    status="FAILED",
                    logs=logs
                )

        if job.subtitles_path:
            try:
                job.subtitles_path = MediaDownloader.prepare_media_path(job.subtitles_path, project_id=job.project_id)
            except Exception as e:
                error_msg = f"Failed to download or prepare subtitles asset ({job.subtitles_path}): {str(e)}"
                logs.append(error_msg)
                return RenderTaskResult(
                    render_id=render_id,
                    project_id=job.project_id,
                    timeline_id=job.timeline_id,
                    status="FAILED",
                    logs=logs
                )

        val_assets = RenderValidatorService.validate_scene_assets(job.scenes)
        logs.extend([f"WARNING: {w}" for w in val_assets.warnings])

        if not val_assets.is_valid:
            error_msg = f"Scene validation failed: {'; '.join(val_assets.errors)}"
            logs.append(error_msg)
            return RenderTaskResult(
                render_id=render_id,
                project_id=job.project_id,
                timeline_id=job.timeline_id,
                status="FAILED",
                logs=logs
            )

        os.makedirs(job.output_dir, exist_ok=True)
        final_video_path = os.path.join(job.output_dir, "final.mp4")
        thumbnail_path = os.path.join(job.output_dir, "thumbnail.jpg")

        total_duration = sum(s.duration_seconds for s in job.scenes)
        w = rendering_settings.video.width
        h = rendering_settings.video.height
        fps = rendering_settings.video.fps

        with tempfile.TemporaryDirectory(prefix="kidsai_render_") as temp_dir:
            logs.append(f"Created temporary working workspace: {temp_dir}")
            rendered_scene_clips: List[str] = []

            # 2. Process Camera Motion for Each Scene
            for sc in job.scenes:
                scene_clip_path = os.path.join(temp_dir, f"scene_{sc.scene_number:03d}.mp4")
                logs.append(f"Rendering Scene {sc.scene_number} ({sc.camera_direction.value}, {sc.duration_seconds}s)...")

                if not sc.image_path or not os.path.isfile(sc.image_path):
                    error_msg = f"Scene {sc.scene_number} media asset missing or unreadable at path: '{sc.image_path}'"
                    logs.append(error_msg)
                    return RenderTaskResult(
                        render_id=render_id,
                        project_id=job.project_id,
                        timeline_id=job.timeline_id,
                        status="FAILED",
                        logs=logs
                    )

                ext = os.path.splitext(sc.image_path)[1].lower()
                if ext in (".mp4", ".webm", ".mov", ".mkv"):
                    # Video clip input
                    video_vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
                    args = [
                        "-stream_loop", "-1",
                        "-i", sc.image_path,
                        "-vf", video_vf,
                        "-t", f"{sc.duration_seconds:.2f}",
                        "-c:v", rendering_settings.video.video_codec,
                        "-preset", "ultrafast",
                        "-pix_fmt", rendering_settings.video.pixel_format,
                        "-an",
                        scene_clip_path
                    ]
                else:
                    # Still image input -> zoompan camera filter
                    camera_vf = CameraEngine.build_camera_filter(
                        direction=sc.camera_direction,
                        duration_seconds=sc.duration_seconds,
                        width=w,
                        height=h,
                        fps=fps,
                        zoom_ratio=sc.camera_zoom
                    )

                    args = [
                        "-loop", "1",
                        "-i", sc.image_path,
                        "-vf", camera_vf,
                        "-t", f"{sc.duration_seconds:.2f}",
                        "-c:v", rendering_settings.video.video_codec,
                        "-preset", "ultrafast",
                        "-pix_fmt", rendering_settings.video.pixel_format,
                        "-an",
                        scene_clip_path
                    ]

                try:
                    FFmpegEngine.run_command(args, timeout=120)
                    rendered_scene_clips.append(scene_clip_path)
                except FFmpegExecutionError as e:
                    logs.append(f"ERROR rendering Scene {sc.scene_number}: {e.stderr}")
                    return RenderTaskResult(
                        render_id=render_id,
                        project_id=job.project_id,
                        timeline_id=job.timeline_id,
                        status="FAILED",
                        logs=logs
                    )

            # 3. Apply Scene Transitions & Concatenate Video Clips
            concatenated_video_path = os.path.join(temp_dir, "video_concatenated.mp4")

            if len(rendered_scene_clips) == 1:
                concatenated_video_path = rendered_scene_clips[0]
            else:
                # Build complex filtergraph for multi-scene xfade transitions
                logs.append("Applying scene transitions and building master video track...")

                filter_parts: List[str] = []
                input_args: List[str] = []

                for idx, clip in enumerate(rendered_scene_clips):
                    input_args.extend(["-i", clip])

                current_offset = 0.0
                last_stream = "[0:v]"

                for idx in range(len(rendered_scene_clips) - 1):
                    sc = job.scenes[idx]
                    next_stream = f"[{idx + 1}:v]"
                    out_stream = f"[v_trans_{idx}]" if idx < len(rendered_scene_clips) - 2 else "[v_master]"
                    current_offset += sc.duration_seconds - sc.transition_duration_seconds

                    xfade_expr = TransitionEngine.build_xfade_filter(
                        stream_a=last_stream,
                        stream_b=next_stream,
                        output_stream=out_stream,
                        transition=sc.transition,
                        duration_sec=sc.transition_duration_seconds,
                        offset_sec=max(0.0, current_offset)
                    )
                    filter_parts.append(xfade_expr)
                    last_stream = out_stream

                complex_filter = ";".join(filter_parts)
                concat_args = input_args + [
                    "-filter_complex", complex_filter,
                    "-map", "[v_master]",
                    "-c:v", rendering_settings.video.video_codec,
                    "-preset", "ultrafast",
                    "-pix_fmt", rendering_settings.video.pixel_format,
                    "-an",
                    concatenated_video_path
                ]

                try:
                    FFmpegEngine.run_command(concat_args, timeout=240)
                except FFmpegExecutionError as e:
                    # Fallback to simple concat if complex xfade fails
                    logs.append(f"Xfade complex filter failed, falling back to concat list: {str(e)}")
                    concat_list_path = os.path.join(temp_dir, "concat.txt")
                    with open(concat_list_path, "w", encoding="utf-8") as f:
                        for clip in rendered_scene_clips:
                            f.write(f"file '{clip}'\n")

                    concat_args_fb = [
                        "-f", "concat",
                        "-safe", "0",
                        "-i", concat_list_path,
                        "-c", "copy",
                        concatenated_video_path
                    ]
                    FFmpegEngine.run_command(concat_args_fb, timeout=120)

            # 4. Subtitle Overlay
            subtitled_video_path = os.path.join(temp_dir, "video_subtitled.mp4")
            sub_filter = None

            if job.subtitles_path and os.path.exists(job.subtitles_path):
                logs.append(f"Applying subtitles from {job.subtitles_path}...")
                sub_items = SubtitleEngine.parse_srt_file(job.subtitles_path)
                ass_path = os.path.join(temp_dir, "subtitles.ass")
                SubtitleEngine.generate_ass_subtitle_file(sub_items, ass_path)
                sub_filter = SubtitleEngine.build_subtitle_filter(ass_path)
            else:
                # Collect scene inline subtitles
                all_subs: List[SubtitleItem] = []
                for sc in job.scenes:
                    all_subs.extend(sc.subtitles)
                if all_subs:
                    logs.append(f"Applying {len(all_subs)} scene subtitle cues...")
                    ass_path = os.path.join(temp_dir, "subtitles.ass")
                    SubtitleEngine.generate_ass_subtitle_file(all_subs, ass_path)
                    sub_filter = SubtitleEngine.build_subtitle_filter(ass_path)

            if sub_filter:
                sub_args = [
                    "-i", concatenated_video_path,
                    "-vf", sub_filter,
                    "-c:v", rendering_settings.video.video_codec,
                    "-preset", "ultrafast",
                    "-pix_fmt", rendering_settings.video.pixel_format,
                    "-an",
                    subtitled_video_path
                ]
                try:
                    FFmpegEngine.run_command(sub_args, timeout=180)
                except FFmpegExecutionError as e:
                    logs.append(f"Subtitle overlay warning: {str(e)}. Proceeding without subtitle burn-in.")
                    subtitled_video_path = concatenated_video_path
            else:
                subtitled_video_path = concatenated_video_path

            # 5. Audio Mixing Engine
            logs.append("Processing audio tracks (narration & background music ducking)...")
            mixed_audio_path = os.path.join(temp_dir, "audio_mixed.aac")
            has_narration = False
            has_music = bool(job.music_path and os.path.exists(job.music_path))

            # Combine narration files if present
            narration_files = [sc.narration_path for sc in job.scenes if sc.narration_path and os.path.exists(sc.narration_path)]
            concat_narration_path = os.path.join(temp_dir, "narration_concat.wav")

            if narration_files:
                has_narration = True
                if len(narration_files) == 1:
                    concat_narration_path = narration_files[0]
                else:
                    n_list_path = os.path.join(temp_dir, "narration_list.txt")
                    with open(n_list_path, "w", encoding="utf-8") as f:
                        for n_file in narration_files:
                            f.write(f"file '{n_file}'\n")
                    FFmpegEngine.run_command([
                        "-f", "concat",
                        "-safe", "0",
                        "-i", n_list_path,
                        "-c", "copy",
                        concat_narration_path
                    ], timeout=60)

            # Build audio mix
            audio_inputs = []
            if has_narration:
                audio_inputs.extend(["-i", concat_narration_path])
            if has_music:
                audio_inputs.extend(["-stream_loop", "-1", "-i", job.music_path])

            audio_filter = AudioEngine.build_audio_mix_filter(
                has_narration=has_narration,
                has_music=has_music,
                total_duration_sec=total_duration
            )

            if audio_inputs:
                audio_args = audio_inputs + [
                    "-filter_complex", audio_filter,
                    "-map", "[a_out]",
                    "-t", f"{total_duration:.2f}",
                    "-c:a", rendering_settings.audio.audio_codec,
                    "-b:a", rendering_settings.audio.bitrate,
                    mixed_audio_path
                ]
            else:
                audio_args = [
                    "-f", "lavfi",
                    "-i", f"anullsrc=channel_layout=stereo:sample_rate={rendering_settings.audio.sample_rate}",
                    "-t", f"{total_duration:.2f}",
                    "-c:a", rendering_settings.audio.audio_codec,
                    mixed_audio_path
                ]

            try:
                FFmpegEngine.run_command(audio_args, timeout=180)
            except FFmpegExecutionError as e:
                logs.append(f"Audio mix warning: {str(e)}. Generating silent audio stream.")
                FFmpegEngine.run_command([
                    "-f", "lavfi",
                    "-i", f"anullsrc=channel_layout=stereo:sample_rate={rendering_settings.audio.sample_rate}",
                    "-t", f"{total_duration:.2f}",
                    "-c:a", rendering_settings.audio.audio_codec,
                    mixed_audio_path
                ], timeout=60)

            # 6. Final Video + Audio Encoding (1080p, H.264, AAC, MP4)
            logs.append("Muxing final 1080p MP4 container with H.264 video and AAC audio...")
            final_args = [
                "-i", subtitled_video_path,
                "-i", mixed_audio_path,
                "-c:v", rendering_settings.video.video_codec,
                "-preset", rendering_settings.video.preset,
                "-crf", str(rendering_settings.video.crf),
                "-pix_fmt", rendering_settings.video.pixel_format,
                "-c:a", rendering_settings.audio.audio_codec,
                "-b:a", rendering_settings.audio.bitrate,
                "-shortest",
                final_video_path
            ]
            FFmpegEngine.run_command(final_args, timeout=300)

            # 7. Extract High-Scoring / Middle Frame Thumbnail
            logs.append("Extracting thumbnail.jpg...")
            mid_ts = max(0.5, total_duration / 2.0)
            try:
                ThumbnailEngine.extract_thumbnail(
                    video_path=final_video_path,
                    output_thumbnail_path=thumbnail_path,
                    timestamp_sec=mid_ts
                )
            except Exception as e:
                logs.append(f"Thumbnail generation warning: {str(e)}")

        gen_time = round(time.time() - start_time, 2)
        file_size = os.path.getsize(final_video_path) if os.path.exists(final_video_path) else 0

        logs.append(f"Render completed successfully in {gen_time}s! Output: {final_video_path} ({file_size} bytes)")

        return RenderTaskResult(
            render_id=render_id,
            project_id=job.project_id,
            timeline_id=job.timeline_id,
            status="COMPLETED",
            resolution="1080p",
            codec="H.264",
            output_format="MP4",
            file_size_bytes=file_size,
            final_video_path=final_video_path,
            final_video_url=f"http://localhost:8000/static/renders/{job.project_id}/final.mp4",
            thumbnail_path=thumbnail_path,
            thumbnail_url=f"http://localhost:8000/static/renders/{job.project_id}/thumbnail.jpg",
            generation_time_seconds=gen_time,
            logs=logs
        )
