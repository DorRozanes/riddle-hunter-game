import random
import os
import difflib
import re
import json
import ast
from datetime import datetime
from openai import OpenAI
from enemies.enums.type_locations_for_enemies import PLACE_TYPES
from enemies.services.math_riddles import generate_math_riddle

# --------------------
# Offline fallback riddles
# --------------------
FALLBACK_RIDDLES = [
    {"riddle": "What has to be broken before you can use it?", "answer": "An egg"},
    {"riddle": "I’m tall when I’m young, and I’m short when I’m old. What am I?", "answer": "A candle"},
    {"riddle": "What month of the year has 28 days?", "answer": "All of them"},
    {"riddle": "What is full of holes but still holds water?", "answer": "A sponge"},
    {"riddle": "What question can you never answer yes to?", "answer": "Are you asleep yet?"},
    {"riddle": "I follow you wherever you go, but I never speak; I’m always there but never seen in the light.", "answer": "shadow"},
    {"riddle": "I speak without a mouth and hear without ears. I have nobody, but I come alive when you call.", "answer": "echo"},
    {"riddle": "The more you take, the more you leave behind.", "answer": "footsteps"},
    {"riddle": "I have keys but no locks. I have space but no room. You can enter but can’t go outside.", "answer": "keyboard"},
    {"riddle": "I go up and down stairs without moving.", "answer": "carpet"},
    {"riddle": "I fly without wings, I cry without eyes; wherever I go, darkness follows me.", "answer": "cloud"},
    {"riddle": "I am not alive, but I grow; I don’t have lungs, but I need air; I don’t have a mouth, but water kills me.", "answer": "fire"},
    {"riddle": "I have cities but no houses, forests but no trees, and rivers but no water.", "answer": "map"},
    {"riddle": "I can be cracked, made, told, and played.", "answer": "joke"},
]

# --------------------
# Hugging Face API setup
# --------------------

HF_API_TOKEN = os.getenv("HF_riddle_bot")
HF_MODEL = os.getenv("HF_MODEL")
HF_API_URL = os.getenv("HF_API_URL")

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def get_riddle(location_type):
    """
    Try to fetch a riddle + answer from Hugging Face Inference API.
    We instruct the AI to return JSON so we can parse it easily.
    Falls back to offline riddles if request fails.
    Generates a math riddle offline for the specific place types
    """
    # The AI isn't working! It's caching the answer!!!

    location_info = {}
    # Find location type information
    for item in PLACE_TYPES:
        if item["place_type"]==location_type:
            location_info = item
            break

    if location_info == {}:
        return random.choice(FALLBACK_RIDDLES)

    # For math riddles, generate without API
    if location_info["riddle_description"]=="math":
        return generate_math_riddle()

    prompt = f"""Generate a JSON object with keys "riddle" and "answer".
        {location_info["riddle_description"]}
        The answer must be one or two words.
        Format strictly as a valid JSON: {{\"riddle\": \"...\", \"answer\": \"...\"}}."""
    try:
        print("------> Debug: Trying to create a client")
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=HF_API_TOKEN,
        )
        print("------> Debug: Client created. Sending a request")
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:fireworks-ai",
            temperature=0.8,
            top_p=0.9,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        answer = json.loads(completion.choices[0].message.content)
        try:
            data = json.loads(answer)
        except:
            data = ast.literal_eval(answer)
        if "riddle" in data and "answer" in data:
            return data
    except Exception:
        return random.choice(FALLBACK_RIDDLES)

def normalize_answer(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # remove punctuation
    words = text.split()
    words = [w for w in words if w not in {"a", "an", "the"}]  # remove articles
    return " ".join(words)

def check_answer(user_input, correct_answer, threshold=0.8):
    norm_user = normalize_answer(user_input)
    norm_correct = normalize_answer(correct_answer)
    ratio = difflib.SequenceMatcher(None, norm_user, norm_correct).ratio()
    return ratio >= threshold