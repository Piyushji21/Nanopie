import os
import uuid
import base64
import requests
from flask import Flask, request, render_template, jsonify, url_for, send_file
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Folders
STATIC_FOLDER = "static"
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(os.path.join(STATIC_FOLDER, UPLOAD_FOLDER), exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY required")

# --- Helpers ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_image_from_prompt(prompt):
    """Generate image using Gemini API"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemini-2.5-flash-image-preview"
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
            if chunk.candidates and chunk.candidates[0].content.parts[0].inline_data:
                return chunk.candidates[0].content.parts[0].inline_data.data
        return None
    except Exception as e:
        print("Gemini error:", e)
        return "GENERATION_ERROR"

def mix_images_with_prompt(images, prompt):
    """Mix images using Gemini API"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemini-2.5-flash-image-preview"
        parts = [types.Part.from_text(text=prompt)]
        for img_path in images:
            with open(img_path, "rb") as f:
                parts.append(types.Part.from_inline_data(mime_type="image/jpeg", data=f.read()))
        contents = [types.Content(role="user", parts=parts)]
        config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
            if chunk.candidates and chunk.candidates[0].content.parts[0].inline_data:
                return chunk.candidates[0].content.parts[0].inline_data.data
        return None
    except Exception as e:
        print("Mix error:", e)
        return "GENERATION_ERROR"

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        prompt = request.form.get("prompt", "").strip()
        api_choice = request.form.get("api_choice", "nano")  # 'nano' or 'gemini'
        uploaded_files = request.files.getlist("images")
        uploaded_image_paths = []
        image_urls = []

        # Handle uploads
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
                if api_choice == "nano":
                    save_path = os.path.join(STATIC_FOLDER, UPLOAD_FOLDER, unique_filename)
                    file.save(save_path)
                    uploaded_image_paths.append(save_path)
                    image_urls.append(url_for("static", filename=f"{UPLOAD_FOLDER}/{unique_filename}", _external=True))
                else:
                    save_path = os.path.join(OUTPUT_FOLDER, unique_filename)
                    file.save(save_path)
                    uploaded_image_paths.append(save_path)

        # --- Nano-Banana API ---
        if api_choice == "nano":
            if image_urls:
                resp = requests.post(
                    "https://sii3.moayman.top/api/nano-banana.php",
                    data={"text": prompt, "links": ",".join(image_urls)},
                )
            else:
                resp = requests.get(f"https://sii3.moayman.top/api/nano-banana.php?text={prompt}")

            # Save image
            try:
                image_bytes = base64.b64decode(resp.json().get("image", ""))
            except:
                image_bytes = resp.content

            output_filename = f"nano_{uuid.uuid4()}.png"
            output_path = os.path.join(STATIC_FOLDER, UPLOAD_FOLDER, output_filename)
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            return jsonify({
                "success": True,
                "image_url": url_for("static", filename=f"{UPLOAD_FOLDER}/{output_filename}", _external=True),
                "filename": output_filename
            })

        # --- Gemini API ---
        else:
            if uploaded_image_paths:
                result = mix_images_with_prompt(uploaded_image_paths, prompt)
            else:
                result = generate_image_from_prompt(prompt)

            if result == "GENERATION_ERROR" or not result:
                return jsonify({"success": False, "error": "Failed to generate Gemini image"})

            output_filename = f"generated_{uuid.uuid4()}.png"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_path, "wb") as f:
                f.write(result)

            # Clean up uploaded files
            for path in uploaded_image_paths:
                if os.path.exists(path):
                    os.remove(path)

            return jsonify({
                "success": True,
                "image_url": f"/download/{output_filename}",
                "filename": output_filename
            })

    except Exception as e:
        print(f"Error in generate route: {e}")
        return jsonify({"success": False, "error": "An error occurred while generating the image."})

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
