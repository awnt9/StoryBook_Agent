from pydantic_ai import Agent, RunContext

from app.core.agents.utils import download_and_store_image, load_prompt
from app.core.config import settings
from app.schemas.story_elements import ImageDeps


bg_generator = Agent(
    model=settings.bg_model,
    system_prompt=load_prompt("background_generator.txt"),
    deps_type=ImageDeps,
)


@bg_generator.tool
def generate_background_image(ctx: RunContext[ImageDeps], prompt: str) -> str:
    response = ctx.deps.openai_client.images.generate(
        model=ctx.deps.image_model,
        prompt=prompt,
        n=1,
        size=ctx.deps.image_size,
        quality="standard",
    )

    image = download_and_store_image(response.data[0].url, prompt=prompt)
    return image.url or ""
