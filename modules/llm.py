import openai
import google.generativeai as genai
from modules.config import settings

# Configure OpenAI
openai.api_key = settings.openai_api_key

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

async def stream_openai(prompt: str):
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

async def stream_gemini(prompt: str):
    model = genai.GenerativeModel("gemini-pro")
    response = await model.generate_content_async(prompt, stream=True)
    async for chunk in response:
        if chunk.text:
            yield chunk.text
