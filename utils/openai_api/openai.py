import openai

from config import OPENAI_KEY

import time


async def get_resort(prompt):
    openai.api_key = OPENAI_KEY
    start = time.time()
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    rating = response.choices[0].text.strip()
    return rating, time.time() - start
