from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=[
        "Generate a caption for this image in about 50 words",
        types.Part.from_uri(
            file_uri="https://www.shutterstock.com/image-photo/sun-sets-behind-mountain-ranges-600nw-2479236003.jpg",
            mime_type="image/jpeg"
        ),
    ]
)

print("Response:", response.text)