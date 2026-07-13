"""Cog adapter for rembg with warm, reusable ONNX sessions."""

from pathlib import Path as LocalPath
from threading import Lock

from cog import BaseRunner, Input, Path


MODELS = (
    "isnet-general-use",
    "u2net",
    "u2netp",
    "isnet-anime",
    "birefnet-general",
)


def output_path(model: str) -> LocalPath:
    """Return a stable, safe output name for a validated model id."""
    if model not in MODELS:
        raise ValueError(f"unsupported model: {model}")
    return LocalPath(f"/tmp/appnz-rembg-{model}.png")


class Runner(BaseRunner):
    def setup(self) -> None:
        from rembg import new_session

        self._new_session = new_session
        self._sessions = {"isnet-general-use": new_session("isnet-general-use")}
        self._lock = Lock()

    def _session(self, model: str):
        if model not in MODELS:
            raise ValueError(f"unsupported model: {model}")
        with self._lock:
            if model not in self._sessions:
                self._sessions[model] = self._new_session(model)
            return self._sessions[model]

    def run(
        self,
        image: Path = Input(description="PNG, JPEG, or WebP image"),
        model: str = Input(
            description="Background segmentation model",
            default="isnet-general-use",
            choices=["isnet-general-use", "u2net", "u2netp", "isnet-anime", "birefnet-general"],
        ),
    ) -> Path:
        from rembg import remove

        source = LocalPath(str(image)).read_bytes()
        result = remove(source, session=self._session(model), force_return_bytes=True)
        destination = output_path(model)
        destination.write_bytes(result)
        return Path(destination)
