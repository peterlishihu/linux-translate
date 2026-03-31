import subprocess
import shutil


class ClipboardManager:
    _wl_copy = None
    _wl_paste = None

    @classmethod
    def _find_commands(cls):
        if cls._wl_copy is None:
            cls._wl_copy = shutil.which('wl-copy')
            cls._wl_paste = shutil.which('wl-paste')
        return cls._wl_copy, cls._wl_paste

    @classmethod
    def get_text(cls) -> str:
        _, wl_paste = cls._find_commands()
        if wl_paste:
            try:
                result = subprocess.run(
                    [wl_paste, '--no-newline'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        return ''

    @classmethod
    def set_text(cls, text: str) -> bool:
        wl_copy, _ = cls._find_commands()
        if wl_copy:
            try:
                result = subprocess.run(
                    [wl_copy],
                    input=text,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        return False

    @classmethod
    def is_available(cls) -> bool:
        wl_copy, wl_paste = cls._find_commands()
        return wl_copy is not None and wl_paste is not None
