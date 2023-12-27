import traceback
import g4f

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .schemas import Interaction
from .config import settings
from . import OPENAI_MODELS

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

g4f.debug.logging = True
g4f.check_version = False


async def openai_response(content: str, interaction: Interaction) -> ChatCompletion:
    response = await client.chat.completions.create(
        model=interaction.settings.model,
        messages=[
            {"role": "system", "content": interaction.settings.prompt},
            {"role": "user", "content": content},
        ],
    )
    return response


async def free_response(content: str, interaction: Interaction) -> str:
    response = await g4f.ChatCompletion.create_async(
        model=g4f.ModelUtils.convert[interaction.settings.model],
        messages=[
            {"role": "system", "content": interaction.settings.prompt},
            {"role": "user", "content": content},
        ],
        prompt=content,
    )
    return response


async def generate_ai_response(content: str, interaction: Interaction) -> str:
    try:
        if interaction.settings.model in OPENAI_MODELS and settings.OPENAI_API_KEY:
            print("OpenAI ...")
            response = await openai_response(content, interaction)
            return response.choices[0].message.content
        else:
            print("G4F ...")
            response = await free_response(content, interaction)
            return response
    except Exception:
        traceback.print_exc()
        return "Sorry, an error has been occurred."
