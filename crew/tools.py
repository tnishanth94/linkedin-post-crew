from dotenv import load_dotenv
from crewai.tools import BaseTool
import requests
import glob
import base64
import mimetypes
import os
from google import genai
from google.genai import types

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

def generate_azure_dalle_image(prompt: str, style: str = "vivid", size: str = "1024x1024", quality: str = "standard", n: int = 1) -> str:
    """
    Generate an image using Azure DALL-E 3 API and save it to the images folder.
    Returns the file path of the saved image or error message.
    """
    import json
    import uuid
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "dall-e-3")
    api_version = "2024-02-01"
    url = f"{endpoint}"
    print(f"Azure DALL-E API URL: {url}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    valid_styles = ["vivid", "natural"]
    if style not in valid_styles:
        print(f"Invalid style '{style}' for Azure DALL-E. Defaulting to 'vivid'.")
        style = "vivid"

    valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
    if size not in valid_sizes:
        print(f"Invalid size '{size}' for Azure DALL-E. Defaulting to '1024x1024'.")
        size = "1024x1024"
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": size,
        "style": style,
        "quality": quality,
        "n": n
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(f"Azure DALL-E API error: {response.status_code}\nResponse text: {response.text}")
        return f"Azure DALL-E API error: {response.status_code} {response.text}"
    try:
        data = response.json()
    except Exception as e:
        print(f"Error parsing JSON response: {e}\nRaw response: {response.text}")
        return f"Error parsing JSON response: {e}\nRaw response: {response.text}"
    images = data.get("data", [])
    if not images:
        print(f"No images generated. Full response: {data}")
        return "No images generated."
    image_url = images[0].get("url")
    if not image_url:
        print(f"No image URL found in response. Full response: {data}")
        return "No image URL found in response."
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        print(f"Image download error: {image_response.status_code}\nResponse text: {image_response.text}")
        return f"Image download error: {image_response.status_code}"
    images_folder = os.path.join(os.path.dirname(__file__), '..', 'images')
    os.makedirs(images_folder, exist_ok=True)
    file_name = f"azure_dalle_{uuid.uuid4().hex}.png"
    file_path = os.path.join(images_folder, file_name)
    with open(file_path, 'wb') as f:
        f.write(image_response.content)
    return file_path

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

def generate_poster(text: str, style: str = "LinkedIn post aesthetic", size: str = "1K") -> str:
    """
    Generate an image poster from text content and style, save to disk, and return file path.
    Uses Google AI Studio boilerplate for image generation.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    prompt = f"Create a visually appealing poster for a LinkedIn post. Style: {style}. Content: {text}."
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    file_index = 0
    image_path = None
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash-image-preview",
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        part = chunk.candidates[0].content.parts[0]
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            file_name = f"linkedin_poster_{file_index}"
            file_index += 1
            inline_data = part.inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".jpg"
            image_path = f"{file_name}{file_extension}"
            save_binary_file(image_path, data_buffer)
            break
        else:
            print(getattr(chunk, "text", ""))
    return image_path

class ImageInsertTool(BaseTool):
    name: str = "InsertImage"
    description: str = "Inserts an image from the local images folder. Returns the file path."

    def _run(self, image_name: str = None) -> str:
        images_folder = os.path.join(os.path.dirname(__file__), '..', 'images')
        if image_name:
            image_path = os.path.join(images_folder, image_name)
            if os.path.exists(image_path):
                return image_path
            else:
                return f"Image {image_name} not found."
        else:
            images = glob.glob(os.path.join(images_folder, '*'))
            if images:
                return images[0]
            else:
                return "No images found in images folder."
