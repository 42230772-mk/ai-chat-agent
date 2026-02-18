import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_claude_reply(user_message: str, weather_result: str = None) -> str:
    """
    Sends the user message to Groq and returns its reply.
    If a weather_result is provided, it's included as context.
    """
    if weather_result:
        system_prompt = (
            "You are a helpful assistant. "
            "The user asked about weather and here is the live weather data: "
            f"{weather_result}. "
            "Use this data to give a friendly, natural response."
        )
    else:
        system_prompt = (
            "You are a helpful assistant. "
            "You can help users get current weather by asking them to specify a city. "
            "Be friendly and conversational."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=512,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
    )

    return response.choices[0].message.content