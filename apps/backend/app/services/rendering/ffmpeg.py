"""
FFmpeg Subprocess Execution Engine.
Safely manages FFmpeg binary discovery, subprocess invocation, error logging, and execution timeouts.
"""

import shutil
import subprocess
import os
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger("ffmpeg_engine")


class FFmpegExecutionError(Exception):
    def __init__(self, message: str, stderr: str = "", command: Optional[List[str]] = None):
        super().__init__(message)
        self.stderr = stderr
        self.command = command or []


class FFmpegNotFoundError(FFmpegExecutionError):
    pass


class FFmpegEngine:
    _cached_exe: Optional[str] = None

    @classmethod
    def get_ffmpeg_path(cls) -> str:
        """Locates system ffmpeg or imageio-ffmpeg binary with environment override support."""
        # 1. Check FFMPEG_PATH environment variable override
        env_ffmpeg = os.getenv("FFMPEG_PATH")
        if env_ffmpeg and os.path.isfile(env_ffmpeg) and os.access(env_ffmpeg, os.X_OK):
            cls._cached_exe = env_ffmpeg
            return env_ffmpeg

        if cls._cached_exe and os.path.isfile(cls._cached_exe) and os.access(cls._cached_exe, os.X_OK):
            return cls._cached_exe

        # 2. Check system PATH lookup
        sys_ffmpeg = shutil.which("ffmpeg")
        if sys_ffmpeg:
            cls._cached_exe = sys_ffmpeg
            return sys_ffmpeg

        # 3. Check imageio_ffmpeg Python package
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.isfile(exe) and os.access(exe, os.X_OK):
                cls._cached_exe = exe
                return exe
        except Exception:
            pass

        # 4. Check common OS binary paths
        common_paths = [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg",
            "/snap/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe"
        ]
        for p in common_paths:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                cls._cached_exe = p
                return p

        raise FFmpegNotFoundError(
            "FFmpeg executable not found. Please install FFmpeg (e.g. 'brew install ffmpeg' on macOS or 'apt install ffmpeg' on Linux) or set the FFMPEG_PATH environment variable."
        )

    @classmethod
    def run_command(
        cls,
        args: List[str],
        timeout: int = 600,
        cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """Runs an FFmpeg command synchronously with timeout and logging."""
        ffmpeg_bin = cls.get_ffmpeg_path()
        full_cmd = [ffmpeg_bin, "-y", "-hide_banner"] + args

        logger.info("Executing FFmpeg command: %s", " ".join(full_cmd))

        try:
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            stdout, stderr = process.communicate(timeout=timeout)
            ret_code = process.returncode

            if ret_code != 0:
                error_msg = f"FFmpeg exited with non-zero code {ret_code}.\nStderr: {stderr[-1000:]}"
                logger.error(error_msg)
                raise FFmpegExecutionError(
                    message=f"FFmpeg command failed with exit code {ret_code}",
                    stderr=stderr,
                    command=full_cmd
                )

            return ret_code, stdout, stderr

        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise FFmpegExecutionError(
                message=f"FFmpeg execution timed out after {timeout} seconds",
                command=full_cmd
            )
        except Exception as e:
            if isinstance(e, FFmpegExecutionError):
                raise e
            raise FFmpegExecutionError(
                message=f"Unexpected error running FFmpeg: {str(e)}",
                command=full_cmd
            )

    @classmethod
    def get_version(cls) -> str:
        """Returns the installed FFmpeg version string."""
        try:
            ret_code, stdout, stderr = cls.run_command(["-version"], timeout=10)
            output = stdout or stderr
            first_line = output.splitlines()[0] if output else "FFmpeg version unknown"
            return first_line
        except FFmpegNotFoundError:
            raise
        except Exception as e:
            return f"Error getting FFmpeg version: {str(e)}"
