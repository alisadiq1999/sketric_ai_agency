import asyncio
import os

import aiohttp
import openai
from pydantic import BaseModel

from voice_assistant.models import ModelName

API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT = openai.OpenAI(api_key=API_KEY)


async def get_model_completion(prompt: str, model: ModelName) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": model.value,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        ) as response:
            if response.status != 200:
                error = await response.text()
                raise RuntimeError(f"OpenAI API error: {error}")
            result = await response.json()
            return result["choices"][0]["message"]["content"]


async def get_structured_output_completion(
    prompt: str, response_format: BaseModel
) -> BaseModel:
    completion = await asyncio.to_thread(
        OPENAI_CLIENT.beta.chat.completions.parse,
        model=ModelName.BASE_MODEL.value,
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
    )
    message = completion.choices[0].message
    if not message.parsed:
        raise ValueError(message.refusal)
    return message.parsed


async def parse_chat_completion(prompt: str, model: ModelName) -> str:
    completion = await asyncio.to_thread(
        OPENAI_CLIENT.beta.chat.completions.parse,
        model=model.value,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content
