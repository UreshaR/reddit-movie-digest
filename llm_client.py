# """
# Groq client. Set your key as an environment variable instead of hardcoding
# it in source (the old grok_client.py had a real key checked into the file
# - rotate that key at https://console.groq.com/keys, it's now exposed).

#     export GROQ_API_KEY="your_key_here"
# """

# import os
# from openai import OpenAI

# client = OpenAI(
#     api_key=os.environ.get("GROQ_API_KEY"),
#     base_url="https://api.groq.com/openai/v1",
# )

# # Pick any current Groq-hosted model, e.g. "llama-3.3-70b-versatile"
# MODEL = "llama-3.3-70b-versatile"


# def ask_groq(prompt, model=MODEL):
#     if not client.api_key:
#         raise RuntimeError(
#             "GROQ_API_KEY is not set. Run: export GROQ_API_KEY=your_key_here"
#         )

#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#     )
#     return response.choices[0].message.content

"""
Groq client. Reads the API key from a .env file (or environment variable)
instead of being hardcoded in source.

Create a .env file in the project root with:
    GROQ_API_KEY=your_key_here
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads .env in the project root and loads it into os.environ

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# Pick any current Groq-hosted model, e.g. "llama-3.3-70b-versatile"
MODEL = "llama-3.3-70b-versatile"


def ask_groq(prompt, model=MODEL):
    if not client.api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to a .env file or run: "
            "$env:GROQ_API_KEY=your_key_here"
        )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content