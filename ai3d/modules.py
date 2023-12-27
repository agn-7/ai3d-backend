import traceback
import g4f
import google.generativeai as genai

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .schemas import Interaction
from .config import settings
from . import OPENAI_MODELS

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
genai.configure(api_key=settings.GEMINI_API_KEY)

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


def gemini_response(content: str, interaction: Interaction) -> str:
    model = genai.GenerativeModel("gemini-pro")
    prompt = interaction.settings.prompt + "\n\n" + content
    response = model.generate_content(prompt)
    return response.text


async def generate_ai_response(content: str, interaction: Interaction) -> str:
    try:
        if interaction.settings.model in OPENAI_MODELS and settings.OPENAI_API_KEY:
            print("OpenAI ...")
            response = await openai_response(content, interaction)
            return response.choices[0].message.content
        elif interaction.settings.model == "gemini-pro":
            print("Gemini ...")
            response = gemini_response(content, interaction)
            return response
        else:
            print("G4F ...")
            response = await free_response(content, interaction)
            return response
    except Exception:
        traceback.print_exc()
        return "Sorry, an error has been occurred."
