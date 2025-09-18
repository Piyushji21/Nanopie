#!/usr/bin/env python3
"""
Test script for Gemini Nano Banana API
This script tests the Gemini 2.5 Flash Image Preview model to generate an image of a banana wearing a costume.
"""

import base64
import mimetypes
import os
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    """Save binary data to a file"""
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}")


def generate():
    """Generate an image using Gemini Nano Banana API"""
    # Get the API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is required.")
        print("Please set it with: export GEMINI_API_KEY='your-api-key-here'")
        return
    
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.5-flash-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Generate an image of a banana wearing a costume."""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )

    print("Generating image with Gemini Nano Banana API...")
    print(f"Model: {model}")
    print("Prompt: Generate an image of a banana wearing a costume.")
    print("-" * 50)

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"nano_banana_costume_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            full_file_name = f"{file_name}{file_extension}"
            save_binary_file(full_file_name, data_buffer)
        else:
            if hasattr(chunk, 'text') and chunk.text:
                print(f"Text response: {chunk.text}")

    print("-" * 50)
    print("Generation complete!")


if __name__ == "__main__":
    try:
        generate()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install google-genai")
