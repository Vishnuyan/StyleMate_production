import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)

def recommend_best_necklace(
    features,
    necklaces
):
    prompt = f"""
User outfit features:

Skin tone:
{features['skin_tone']}

Neckline:
{features['neckline']}

Dress color:
{features['dress_color']}

Available necklaces:
{necklaces}

Choose best matching necklace.

Return only:
necklace id
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content