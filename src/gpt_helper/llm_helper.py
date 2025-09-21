import os
import base64
import random
from PIL import Image
from io import BytesIO
from typing import List
from loguru import logger
from openai import OpenAI

from data.prompts import generate_appearance_generating_prompt
from src.utils import get_creature_appearance_path, get_image_in_b64_format

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_llm_clients(api_file_path: str, base_url: str | None, llm_name: str, llm_model: str) -> None:
    with open(api_file_path, "r", encoding="utf-8") as f:
        api_list = f.read().splitlines()

    for api in api_list:
        new_llm_client = OpenAI(
            api_key=api,
            base_url=base_url,
        )

        llm_clients.append(
            {
                "name": llm_name,
                "client": new_llm_client,
                "model": llm_model
            }
        )

        logger.info(f"Created new {llm_name} LLM client.")

llm_clients = list()
setup_llm_clients(
    os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "llm_api", "openai_api.txt")),
    None,
    "OPENAI",
    "gpt-4o"
)
# setup_llm_clients(
#     os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "llm_api", "hyperbolic_api.txt")),
#     "https://api.hyperbolic.xyz/v1",
#     "HYPERBOLIC",
#     "meta-llama/Meta-Llama-3.1-70B-Instruct"
# )
# setup_llm_clients(
#     os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "llm_api", "nous_api.txt")),
#     "https://inference-api.nousresearch.com/v1",
#     "NOUS",
#     "Hermes-3-Llama-3.1-70B"
# )

#openai client for images
with open(os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "llm_api", "openai_api.txt")), "r", encoding="utf-8") as f:
    api_list = f.read().splitlines()
openai_client = OpenAI(api_key=api_list[0])


def fetch_llm_response(client: OpenAI, messages, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating response from OpenAI: {e}")
        raise

def fetch_ai_response(content: List):
    try:
        messages = [{"role": "user", "content": content}]
        random_llm_client = random.choice(llm_clients)
        return fetch_llm_response(random_llm_client['client'], messages, random_llm_client['model'])
    except Exception as e:
        logger.error(f"Error generating response from OpenAI: {e}")
        raise


def generate_creature_appearance(chat_id: str) -> str:
    try:
        response = openai_client.images.generate(
            model="gpt-image-1",
            prompt=generate_appearance_generating_prompt(chat_id),
            n=1,  # Number of images to generate
            size="1024x1024"
        )

        # Get the generated image URL
        image_base64 = response.data[0].b64_json

        character_appearance_path = get_creature_appearance_path(chat_id)

        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))
        image.save(character_appearance_path)

        return character_appearance_path

    except Exception as e:
        logger.error(f"{e}")
        raise


def generate_simple_content(content_message: str, image_path: str = None):
    content = []

    # text
    content.append({
        "type": "text",
        "text": content_message
    })

    # image
    if image_path:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{get_image_in_b64_format(image_path)}"}
        })
    return content