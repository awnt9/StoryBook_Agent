from __future__ import annotations

from pathlib import Path
from string import Formatter
from urllib.request import urlopen
from uuid import uuid4

from app.schemas.story_elements import Image


APP_DIR = Path(__file__).resolve().parents[1]
IMAGES_DIR = APP_DIR / "images"


def build_image_url(image_id: str) -> str:
    return f"/api/v1/images/{image_id}"


def photo_to_image(
    photo_bytes: bytes,
    extension: str = "png",
    *,
    prompt: str | None = None,
) -> Image:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    image_id = f"img_{uuid4().hex}"
    filename = f"{image_id}.{extension.lstrip('.')}"
    path = IMAGES_DIR / filename

    path.write_bytes(photo_bytes)

    return Image(
        image_id=image_id,
        path=str(path),
        url=build_image_url(image_id),
        prompt=prompt,
        description=None,
    )


def download_and_store_image(source_url: str, *, prompt: str | None = None) -> Image:
    with urlopen(source_url) as response:
        photo_bytes = response.read()

    return photo_to_image(photo_bytes, prompt=prompt)


def image_to_photo(image: Image) -> bytes:
    if image.path is not None:
        path = Path(image.path)

        if not path.exists():
            raise FileNotFoundError(f"Image path does not exist: {image.path}")

        return path.read_bytes()

    if image.image_id is not None:
        matches = list(IMAGES_DIR.glob(f"{image.image_id}.*"))

        if not matches:
            raise FileNotFoundError(f"Image id not found in {IMAGES_DIR}: {image.image_id}")

        return matches[0].read_bytes()

    raise ValueError("Image must have either path or image_id.")


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


class _SafePromptValues(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return f"[No aplica: {key}]"


def load_prompt(prompt_name: str, **placeholders: str) -> str:
    prompt_path = PROMPTS_DIR / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    template = prompt_path.read_text(encoding="utf-8")
    return Formatter().vformat(template, (), _SafePromptValues(placeholders))