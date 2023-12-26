import traceback
import g4f

from .schemas import Interaction
from .config import settings

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

g4f.debug.logging = True
g4f.check_version = False


async def openai_response(content: str, interaction: Interaction) -> ChatCompletion:
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


async def free_response(content: str, interaction: Interaction) -> str:
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.ModelUtils.convert[interaction.settings.model],
            messages=[
                {"role": "system", "content": interaction.settings.prompt},
                {"role": "user", "content": content},
            ],
            prompt=content,
        )
        return response
    except Exception:
        traceback.print_exc()
        return "error!"


async def generate_ai_response(content: str, interaction: Interaction) -> str:
    if "gpt" in interaction.settings.model and settings.OPENAI_API_KEY:
        response = await openai_response(content, interaction)
        return response.choices[0].message.content
    else:
        response = await free_response(content, interaction)
        return response
