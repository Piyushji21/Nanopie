# Nano Banana Image Mixer Web App

A beautiful web application for generating and mixing images using Google's Gemini 2.5 Flash Image Preview API. This app allows you to either generate new images from text prompts or mix multiple uploaded images with custom prompts.

## Features

- 🎨 **Text-to-Image Generation**: Create images from detailed text prompts
- 🖼️ **Image Mixing**: Upload 1-5 images and mix them with custom prompts
- 📱 **Responsive Design**: Beautiful, modern UI that works on all devices
- ⬇️ **Download Support**: Download generated images directly
- 🎯 **Drag & Drop**: Easy file upload with drag and drop functionality
- ⚡ **Real-time Preview**: See uploaded images before processing

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

You need to set your Google AI API key as an environment variable:

**Option 1: Using environment variable**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Option 2: Using .env file (recommended)**
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your actual API key:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

**To get your API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it as shown above

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Text-to-Image Generation
1. Enter a detailed prompt describing the image you want to generate
2. Click "Generate Image"
3. Wait for the AI to create your image
4. Download the result

### Image Mixing
1. Upload 1-5 images using the file upload area
2. Enter a prompt describing how you want to mix the images
3. Click "Generate Image"
4. Download the mixed result

## Tips for Better Results

- **Be Descriptive**: Use detailed, specific prompts for better results
- **Include Style**: Mention artistic styles, lighting, composition
- **Specify Details**: Include colors, mood, setting, and other visual elements

### Example Prompts

**For Text-to-Image:**
```
A photorealistic portrait of a wise elderly wizard with a long white beard, wearing a deep blue robe with silver stars, standing in a mystical library with floating books and glowing crystals, dramatic lighting with warm golden tones, highly detailed, 8K resolution
```

**For Image Mixing:**
```
Combine these images to create a professional product advertisement with a modern, clean aesthetic. Blend the colors harmoniously and create a cohesive composition that highlights the main subject.
```

## File Structure

```
Nano Banana/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface template
├── uploads/              # Temporary uploaded files
├── output/               # Generated images
├── static/               # Static assets
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Integration

This app uses Google's Gemini 2.5 Flash Image Preview API for:
- Text-to-image generation
- Image mixing and remixing
- High-quality image processing

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

### Common Issues

1. **"Failed to generate image"**: Check your internet connection and API key
2. **File upload errors**: Ensure files are in supported formats (PNG, JPG, JPEG, GIF, BMP, WEBP)
3. **Large file uploads**: Maximum file size is 16MB per file

### Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- WEBP

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!
