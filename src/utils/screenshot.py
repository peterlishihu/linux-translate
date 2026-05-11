# src/utils/screenshot.py
import subprocess
import shutil
import tempfile
import os


class ScreenshotManager:
    """Screenshot capture utility for Wayland using grim + slurp."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if grim and slurp are installed."""
        return (shutil.which('grim') is not None and
                shutil.which('slurp') is not None)

    @classmethod
    def capture_region(cls) -> str | None:
        """Let user select a screen region, capture it, return temp file path.

        Returns None if user cancels or tools are missing.
        """
        if not cls.is_available():
            return None

        try:
            # Run slurp to get geometry
            slurp_result = subprocess.run(
                ['slurp'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if slurp_result.returncode != 0:
                return None  # User cancelled

            geometry = slurp_result.stdout.strip()
            if not geometry:
                return None

            # Capture region with grim
            tmp_file = tempfile.mktemp(suffix='.png', prefix='translate_ocr_')
            grim_result = subprocess.run(
                ['grim', '-g', geometry, tmp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            if grim_result.returncode == 0 and os.path.exists(tmp_file):
                return tmp_file

            # Cleanup on failure
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
            return None

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    @classmethod
    def capture_fullscreen(cls) -> str | None:
        """Capture full screen, return temp file path."""
        if not cls.is_available():
            return None

        try:
            tmp_file = tempfile.mktemp(suffix='.png', prefix='translate_ocr_')
            result = subprocess.run(
                ['grim', tmp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and os.path.exists(tmp_file):
                return tmp_file

            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
            return None

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None
