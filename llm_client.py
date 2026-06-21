"""
Groq client. Set your key as an environment variable instead of hardcoding
it in source (the old grok_client.py had a real key checked into the file
- rotate that key at https://console.groq.com/keys, it's now exposed).

    export GROQ_API_KEY="your_key_here"
"""

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# Pick any current Groq-hosted model, e.g. "llama-3.3-70b-versatile"
MODEL = "llama-3.3-70b-versatile"


def ask_groq(prompt, model=MODEL):
    if not client.api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Run: export GROQ_API_KEY=your_key_here"
        )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content
