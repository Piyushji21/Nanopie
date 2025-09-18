import os
import base64
import uuid
import mimetypes
from io import BytesIO
from flask import Flask, request, render_template, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types
from PIL import Image
import tempfile
import shutil

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure the API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it with your Google AI API key.")

# Create necessary directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_image_from_prompt(prompt):
    """Generate an image from text prompt using Gemini 2.5 Flash Image Preview"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemini-2.5-flash-image-preview"
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

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
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                return data_buffer
        
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating image: {e}")
        
        # Handle specific quota errors
        if "429" in error_msg or "quota" in error_msg.lower():
            return "QUOTA_EXCEEDED"
        elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "INVALID_API_KEY"
        else:
            return "GENERATION_ERROR"

def mix_images_with_prompt(images, prompt):
    """Mix multiple images with a prompt using Gemini 2.5 Flash Image Preview"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemini-2.5-flash-image-preview"
        
        # Prepare the content with images and prompt
        parts = [types.Part.from_text(text=prompt)]
        for image_path in images:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            parts.append(types.Part.from_inline_data(
                mime_type='image/jpeg',
                data=image_data
            ))
        
        contents = [
            types.Content(
                role="user",
                parts=parts,
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

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
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                return data_buffer
        
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"Error mixing images: {e}")
        
        # Handle specific quota errors
        if "429" in error_msg or "quota" in error_msg.lower():
            return "QUOTA_EXCEEDED"
        elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "INVALID_API_KEY"
        else:
            return "GENERATION_ERROR"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.form.get('prompt', '').strip()
        uploaded_files = request.files.getlist('images')
        
        if not prompt:
            flash('Please enter a prompt', 'error')
            return redirect(url_for('index'))
        
        # Handle uploaded images
        uploaded_image_paths = []
        if uploaded_files and uploaded_files[0].filename:
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    uploaded_image_paths.append(file_path)
        
        # Generate or mix images
        if uploaded_image_paths:
            # Mix uploaded images with prompt
            if not prompt:
                prompt = "Combine these images in a way that makes sense."
            result = mix_images_with_prompt(uploaded_image_paths, prompt)
        else:
            # Generate new image from prompt only
            result = generate_image_from_prompt(prompt)
        
        # Handle different result types
        if result == "QUOTA_EXCEEDED":
            return jsonify({
                'success': False,
                'error': 'API quota exceeded. Please wait for quota reset or use a different API key. Free tier quotas reset daily.'
            })
        elif result == "INVALID_API_KEY":
            return jsonify({
                'success': False,
                'error': 'Invalid API key. Please check your Google AI API key.'
            })
        elif result == "GENERATION_ERROR":
            return jsonify({
                'success': False,
                'error': 'Failed to generate image. Please try again with a different prompt.'
            })
        elif result and isinstance(result, bytes):
            # Save the generated image
            unique_filename = f"generated_{uuid.uuid4()}.png"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], unique_filename)
            
            with open(output_path, 'wb') as f:
                f.write(result)
            
            # Clean up uploaded files
            for path in uploaded_image_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            return jsonify({
                'success': True,
                'image_url': f'/download/{unique_filename}',
                'filename': unique_filename
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate image. Please try again.'
            })
            
    except Exception as e:
        print(f"Error in generate route: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating the image.'
        })

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error downloading file: {e}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/view/<filename>')
def view_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        print(f"Error viewing file: {e}")
        return "Error viewing file", 500

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return empty response with 204 No Content status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
