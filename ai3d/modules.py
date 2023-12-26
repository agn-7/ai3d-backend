import traceback

from .schemas import Interaction
from .config import settings

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_ai_response(
    content: str, interaction: Interaction
) -> ChatCompletion:
    try:
        response = await client.chat.completions.create(
            model=interaction.settings.model,
            messages=[
                {"role": "system", "content": interaction.settings.prompt},
                {"role": "user", "content": content},
            ],
        )
        return response
    except Exception:
        traceback.print_exc()
        return "error!"
