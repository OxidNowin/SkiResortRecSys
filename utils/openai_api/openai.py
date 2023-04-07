import openai

from config import OPENAI_KEY


async def get_resort(text):
    openai.api_key = OPENAI_KEY
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        max_tokens=1500
    )
    rating = response.choices[0].text.strip()
    print(response)
    return rating
