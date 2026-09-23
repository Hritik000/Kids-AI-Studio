"""Deterministic local media helpers for mock providers."""

import os
import struct
import tempfile
import zlib


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def create_mock_png(
    project_id: str,
    asset_name: str,
    width: int,
    height: int,
    color: tuple[int, int, int] = (26, 29, 39),
) -> str:
    """Create a small, valid local PNG without external services or image dependencies."""
    width = max(1, int(width))
    height = max(1, int(height))
    assets_dir = os.path.join(tempfile.gettempdir(), "kidsai_renders", project_id, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    png_path = os.path.join(assets_dir, asset_name)

    if os.path.isfile(png_path) and os.path.getsize(png_path) > 0:
        return png_path

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    scanline = b"\x00" + bytes(color) * width
    image_data = zlib.compress(scanline * height, 9)
    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", header),
            _png_chunk(b"IDAT", image_data),
            _png_chunk(b"IEND", b""),
        ]
    )

    with open(png_path, "wb") as png_file:
        png_file.write(png)
    os.chmod(png_path, 0o644)
    return png_path
