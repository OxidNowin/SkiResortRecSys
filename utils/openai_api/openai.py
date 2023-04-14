import openai

from config import OPENAI_KEY


async def get_resort(prompt):
    openai.api_key = OPENAI_KEY
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.1,
    )
    rating = response.choices[0].text.strip()
    print(response)
    return rating
