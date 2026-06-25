from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from mimetypes import guess_type
from pathlib import Path

from .errors import InvalidInspectionInput
from .types import InspectionInput


@dataclass(frozen=True)
class InputPreparer:
    def prepare_path(
        self, source_path: str | Path, media_type: str | None = None
    ) -> InspectionInput:
        path = Path(source_path).expanduser().resolve()
        if not path.exists():
            raise InvalidInspectionInput(f"inspection input does not exist: {path}")
        if not path.is_file():
            raise InvalidInspectionInput(f"inspection input is not a file: {path}")

        content = path.read_bytes()
        detected_media_type = media_type or guess_type(path.name)[0]
        if detected_media_type is None:
            raise InvalidInspectionInput("inspection input media type is unknown")

        return InspectionInput(
            source_path=path,
            content_sha256=sha256(content).hexdigest(),
            media_type=detected_media_type,
            size_bytes=len(content),
        )

