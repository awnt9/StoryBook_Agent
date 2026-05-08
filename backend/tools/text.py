from schemas import Scene, StoryState
from tools.story import write_scene


def generate_text(
    state: StoryState,
    user_message: str | None = None,
) -> Scene:
    brief = user_message or "Continua la historia con una nueva escena coherente."
    return write_scene(state=state, brief=brief)
